import datetime
import glob
import logging
import os
import re
import shutil
import subprocess


logger = logging.getLogger("Artifact")

file_url_regex = re.compile(r"^file://(?P<host>[a-zA-Z0-9_\-\.]*)/(?P<path>([a-zA-Z]:)?[a-zA-Z0-9_\-\./]+)$")
ssh_url_regex = re.compile(r"^ssh://(?P<user>[a-zA-Z0-9_\-]+)@(?P<host>[a-zA-Z0-9_\-\.]+):(?P<path>[a-zA-Z0-9_\-\./]+)$")


def create_artifact_server_client(server_url, server_parameters, environment):
    if server_url.startswith("file://"):
        return ArtifactServerFileClient(**file_url_regex.search(server_url).groupdict())

    if server_url.startswith("ssh://"):
        client = ArtifactServerSshClient(**ssh_url_regex.search(server_url).groupdict())
        client.ssh_executable = environment["ssh_executable"]
        client.scp_executable = environment["scp_executable"]
        client.ssh_parameters = server_parameters.get("ssh_parameters", [])
        return client

    raise ValueError("Unsupported server url: '%s'" % server_url)



class ArtifactServerFileClient:
    """ Client for an artifact server using file system operations """


    def __init__(self, host, path):
        if host is None or host == "":
            self.server_path = os.path.normpath(path)
        else:
            self.server_path = "\\\\" + host + "\\" + os.path.normpath(path)


    def check_access(self):
        if not os.path.exists(self.server_path):
            raise RuntimeError("Artifact server is unreachable")


    def exists(self, repository, path_in_repository, artifact_name, file_extension):
        remote_artifact_path = os.path.join(self.server_path, repository, path_in_repository, artifact_name)
        return os.path.exists(remote_artifact_path + file_extension)


    def list_files(self, repository, path_in_repository, artifact_pattern, file_extension):
        artifact_directory = os.path.join(self.server_path, repository, path_in_repository)
        all_artifact_paths = glob.glob(os.path.join(artifact_directory, artifact_pattern + file_extension))
        return [ os.path.basename(path[ : - len(file_extension) ]) for path in all_artifact_paths ]


    def list_files_with_metadata(self, repository, path_in_repository, artifact_pattern, file_extension):
        name_collection = self.list_files(repository, path_in_repository, artifact_pattern, file_extension)

        file_entry_collection = []
        for file_name in name_collection:
            file_path = os.path.join(self.server_path, repository, path_in_repository, file_name + file_extension)
            modification_date = datetime.datetime.utcfromtimestamp(os.path.getmtime(file_path)).replace(microsecond = 0).isoformat() + "Z"
            file_entry = { "name": file_name, "update_date": modification_date }
            file_entry_collection.append(file_entry)

        return file_entry_collection


    def list_directories(self, repository, directory_pattern):
        return [ os.path.basename(path) for path in glob.glob(os.path.join(self.server_path, repository, directory_pattern)) if os.path.isdir(path) ]


    def create_directory(self, repository, path_in_repository, simulate = False):
        directory_path = os.path.join(self.server_path, repository, path_in_repository)
        if not simulate:
            os.makedirs(directory_path, exist_ok = True)


    def upload(self, # pylint: disable = too-many-arguments
            local_repository, remote_repository, path_in_repository, artifact_name, file_extension, overwrite = False, simulate = False):

        logger.info("Uploading artifact '%s' to repository '%s'",
            artifact_name, os.path.join(self.server_path, remote_repository))

        local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
        remote_artifact_path = os.path.join(self.server_path, remote_repository, path_in_repository, artifact_name)

        if not simulate and not os.path.exists(local_artifact_path + file_extension):
            raise ValueError("Local artifact does not exist: '%s'" % local_artifact_path)
        if not overwrite and self.exists(remote_repository, path_in_repository, artifact_name, file_extension):
            raise ValueError("Remote artifact already exists: '%s'" % remote_artifact_path)

        self.create_directory(remote_repository, path_in_repository, simulate = simulate)

        logger.info("Copying '%s' to '%s'", local_artifact_path + file_extension, remote_artifact_path + file_extension)
        if not simulate:
            shutil.copyfile(local_artifact_path + file_extension, remote_artifact_path + file_extension + ".tmp")
            os.replace(remote_artifact_path + file_extension + ".tmp", remote_artifact_path + file_extension)


    def download(self, # pylint: disable = too-many-arguments
            local_repository, remote_repository, path_in_repository, artifact_name, file_extension, simulate = False):

        logger.info("Downloading artifact '%s' from repository '%s'",
            artifact_name, os.path.join(self.server_path, remote_repository))

        local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
        remote_artifact_path = os.path.join(self.server_path, remote_repository, path_in_repository, artifact_name)

        if not simulate:
            os.makedirs(os.path.dirname(local_artifact_path), exist_ok = True)

        logger.info("Copying '%s' to '%s'", remote_artifact_path + file_extension, local_artifact_path + file_extension)
        if not simulate:
            shutil.copyfile(remote_artifact_path + file_extension, local_artifact_path + file_extension + ".tmp")
            os.replace(local_artifact_path + file_extension + ".tmp", local_artifact_path + file_extension)


    def delete(self, # pylint: disable = too-many-arguments
            repository, path_in_repository, artifact_name, file_extension, simulate = False):
        logger.info("Deleting artifact '%s'", artifact_name)
        file_path = os.path.join(self.server_path, repository, path_in_repository, artifact_name + file_extension)
        if not simulate:
            os.remove(file_path)


    def delete_empty_directories(self, repository, path_in_repository, simulate = False):
        current_directory = os.path.join(self.server_path, repository)
        if path_in_repository is not None:
            current_directory = os.path.join(current_directory, path_in_repository)

        for file_entry in os.listdir(current_directory):
            if os.path.isdir(os.path.join(current_directory, file_entry)):
                self.delete_empty_directories(repository, os.path.join(current_directory, file_entry), simulate = simulate)

        if len(os.listdir(current_directory)) == 0:
            if not simulate:
                os.rmdir(current_directory)



class ArtifactServerSshClient:
    """ Client for an artifact server using SSH operations """


    def __init__(self, user, host, path):
        self.server_user = user
        self.server_host = host
        self.server_path = path

        self.ssh_executable = "ssh"
        self.scp_executable = "scp"
        self.ssh_parameters = []


    def exists(self, repository, path_in_repository, artifact_name, file_extension):
        remote_artifact_path = self.server_path + "/" + repository + "/" + path_in_repository + "/" + artifact_name

        exists_command = [ self.ssh_executable ] + self.ssh_parameters + [ self.server_user + "@" + self.server_host ]
        exists_command += [ "[[ -f %s ]]" % (remote_artifact_path + file_extension) ]

        logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in exists_command))
        exists_result = subprocess.call(exists_command)
        if exists_result == 255:
            raise RuntimeError("Failed to connect to the SSH server")

        return exists_result == 0


    def create_directory(self, repository, path_in_repository, simulate = False):
        mkdir_command = [ self.ssh_executable ] + self.ssh_parameters + [ self.server_user + "@" + self.server_host ]
        mkdir_command += [ "mkdir --parents %s" % (self.server_path + "/" + repository + "/" + path_in_repository) ]

        logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in mkdir_command))
        if not simulate:
            mkdir_result = subprocess.call(mkdir_command)
            if mkdir_result == 255:
                raise RuntimeError("Failed to connect to the SSH server")
            if mkdir_result != 0:
                raise RuntimeError("Failed to create directory: '%s'" % path_in_repository)


    def upload(self, # pylint: disable = too-many-arguments
            local_repository, remote_repository, path_in_repository, artifact_name, file_extension, overwrite = False, simulate = False):

        logger.info("Uploading artifact '%s' to repository '%s'",
            artifact_name, "ssh://" + self.server_host + ":" + self.server_path + "/" + remote_repository)

        local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
        remote_artifact_path = self.server_path + "/" + remote_repository + "/" + path_in_repository + "/" + artifact_name

        if not simulate and not os.path.exists(local_artifact_path + file_extension):
            raise ValueError("Local artifact does not exist: '%s'" % local_artifact_path)
        if not overwrite and self.exists(remote_repository, path_in_repository, artifact_name, file_extension):
            raise ValueError("Remote artifact already exists: '%s'" % remote_artifact_path)

        self.create_directory(remote_repository, path_in_repository, simulate = simulate)

        upload_command = [ self.scp_executable ] + self.ssh_parameters
        upload_command += [ local_artifact_path + file_extension ]
        upload_command += [ self.server_user + "@" + self.server_host + ":" + remote_artifact_path + file_extension + ".tmp" ]

        logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in upload_command))
        if not simulate:
            upload_result = subprocess.call(upload_command)
            if upload_result == 255:
                raise RuntimeError("Failed to connect to the SSH server")
            if upload_result != 0:
                raise RuntimeError("Failed to upload the artifact")

        move_command = [ self.ssh_executable ] + self.ssh_parameters + [ self.server_user + "@" + self.server_host ]
        move_command += [ "mv %s %s" % (remote_artifact_path + file_extension + ".tmp", remote_artifact_path + file_extension) ]

        logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in move_command))
        if not simulate:
            move_result = subprocess.call(move_command)
            if move_result == 255:
                raise RuntimeError("Failed to connect to the SSH server")
            if move_result != 0:
                raise RuntimeError("Failed to upload the artifact")


    def download(self, # pylint: disable = too-many-arguments
            local_repository, remote_repository, path_in_repository, artifact_name, file_extension, simulate = False):

        logger.info("Downloading artifact '%s' from repository '%s'",
            artifact_name, "ssh://" + self.server_host + ":" + self.server_path + "/" + remote_repository)

        local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
        remote_artifact_path = self.server_path + "/" + remote_repository + "/" + path_in_repository + "/" + artifact_name

        if not simulate:
            os.makedirs(os.path.dirname(local_artifact_path), exist_ok = True)

        download_command = [ self.scp_executable ] + self.ssh_parameters
        download_command += [ self.server_user + "@" + self.server_host + ":" + remote_artifact_path + file_extension ]
        download_command += [ local_artifact_path + file_extension + ".tmp" ]

        logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in download_command))
        if not simulate:
            download_result = subprocess.call(download_command)
            if download_result == 255:
                raise RuntimeError("Failed to connect to the SSH server")
            if download_result != 0:
                raise RuntimeError("Failed to download the artifact")
            os.replace(local_artifact_path + file_extension + ".tmp", local_artifact_path + file_extension)
