import logging
import os
import re
import shutil
import subprocess


logger = logging.getLogger("Artifact")

file_url_regex = re.compile(r"^file:///(?P<path>([a-zA-Z]:)?[a-zA-Z0-9_\-\./]+)$")
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


	def __init__(self, path):
		self.server_path = os.path.normpath(path)


	def exists(self, repository, path_in_repository, artifact_name, file_extension):
		remote_artifact_path = os.path.join(self.server_path, repository, path_in_repository, artifact_name)
		return os.path.exists(remote_artifact_path + file_extension)


	def create_directory(self, repository, path_in_repository, simulate):
		directory_path = os.path.join(self.server_path, repository, path_in_repository)
		if not simulate:
			os.makedirs(directory_path, exist_ok = True)


	def upload(self, local_repository, remote_repository, path_in_repository, artifact_name, file_extension, overwrite, simulate): # pylint: disable = too-many-arguments
		logger.info("Uploading artifact '%s' to repository '%s'", artifact_name, os.path.join(self.server_path, remote_repository))

		local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
		remote_artifact_path = os.path.join(self.server_path, remote_repository, path_in_repository, artifact_name)

		if not simulate and not os.path.exists(local_artifact_path + file_extension):
			raise ValueError("Local artifact does not exist: '%s'" % local_artifact_path)
		if not overwrite and self.exists(remote_repository, path_in_repository, artifact_name, file_extension):
			raise ValueError("Remote artifact already exists: '%s'" % remote_artifact_path)

		self.create_directory(remote_repository, path_in_repository, simulate)

		logger.info("Copying '%s' to '%s'", local_artifact_path + file_extension, remote_artifact_path + file_extension)
		if not simulate:
			shutil.copyfile(local_artifact_path + file_extension, remote_artifact_path + file_extension + ".tmp")
			shutil.move(remote_artifact_path + file_extension + ".tmp", remote_artifact_path + file_extension)


	def download(self, local_repository, remote_repository, path_in_repository, artifact_name, file_extension, simulate): # pylint: disable = too-many-arguments
		logger.info("Downloading artifact '%s' from repository '%s'", artifact_name, os.path.join(self.server_path, remote_repository))

		local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
		remote_artifact_path = os.path.join(self.server_path, remote_repository, path_in_repository, artifact_name)

		if not simulate:
			os.makedirs(os.path.dirname(local_artifact_path), exist_ok = True)

		logger.info("Copying '%s' to '%s'", remote_artifact_path + file_extension, local_artifact_path + file_extension)
		if not simulate:
			shutil.copyfile(remote_artifact_path + file_extension, local_artifact_path + file_extension + ".tmp")
			shutil.move(local_artifact_path + file_extension + ".tmp", local_artifact_path + file_extension)



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


	def create_directory(self, repository, path_in_repository, simulate):
		mkdir_command = [ self.ssh_executable ] + self.ssh_parameters + [ self.server_user + "@" + self.server_host ]
		mkdir_command += [ "mkdir --parents %s" % (self.server_path + "/" + repository + "/" + path_in_repository) ]

		logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in mkdir_command))
		if not simulate:
			mkdir_result = subprocess.call(mkdir_command)
			if mkdir_result == 255:
				raise RuntimeError("Failed to connect to the SSH server")
			if mkdir_result != 0:
				raise RuntimeError("Failed to create directory: '%s'" % path_in_repository)


	def upload(self, local_repository, remote_repository, path_in_repository, artifact_name, file_extension, overwrite, simulate): # pylint: disable = too-many-arguments
		logger.info("Uploading artifact '%s' to repository '%s'", artifact_name, "ssh://" + self.server_host + ":" + self.server_path + "/" + remote_repository)

		local_artifact_path = os.path.join(local_repository, path_in_repository, artifact_name)
		remote_artifact_path = self.server_path + "/" + remote_repository + "/" + path_in_repository + "/" + artifact_name

		if not simulate and not os.path.exists(local_artifact_path + file_extension):
			raise ValueError("Local artifact does not exist: '%s'" % local_artifact_path)
		if not overwrite and self.exists(remote_repository, path_in_repository, artifact_name, file_extension):
			raise ValueError("Remote artifact already exists: '%s'" % remote_artifact_path)

		self.create_directory(remote_repository, path_in_repository, simulate)

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


	def download(self, local_repository, remote_repository, path_in_repository, artifact_name, file_extension, simulate): # pylint: disable = too-many-arguments
		logger.info("Downloading artifact '%s' from repository '%s'", artifact_name, "ssh://" + self.server_host + ":" + self.server_path + "/" + remote_repository)

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
			shutil.move(local_artifact_path + file_extension + ".tmp", local_artifact_path + file_extension)
