import logging
import os
import shutil
import zipfile


logger = logging.getLogger("Artifact")


class ArtifactRepository:


	def __init__(self, local_path, project_identifier):
		self.local_path = local_path
		self.project_identifier = project_identifier
		self.server_client = None


	def show(self, artifact_name, artifact_files): # pylint: disable = no-self-use
		logger.info("Artifact '%s'", artifact_name)

		for file_path in artifact_files:
			logger.info("+ '%s'", file_path)


	def list_remote(self, path_in_repository, artifact_pattern):
		return self.server_client.list_files(self.project_identifier, path_in_repository, artifact_pattern, ".zip")


	def list_remote_with_metadata(self, path_in_repository, artifact_pattern):
		return self.server_client.list_files_with_metadata(self.project_identifier, path_in_repository, artifact_pattern, ".zip")


	def package(self, path_in_repository, artifact_name, artifact_files, simulate):
		logger.info("Packaging artifact '%s'", artifact_name)

		if len(artifact_files) == 0:
			raise ValueError("The artifact is empty")

		artifact_path = os.path.join(self.local_path, path_in_repository, artifact_name)

		logger.info("Writing '%s'", artifact_path + ".zip")

		if not simulate:
			os.makedirs(os.path.dirname(artifact_path), exist_ok = True)

		if simulate:
			for source, destination in artifact_files:
				logger.info("+ '%s' => '%s'", source, destination)
		else:
			with zipfile.ZipFile(artifact_path + ".zip.tmp", "w", zipfile.ZIP_DEFLATED) as archive_file:
				for source, destination in artifact_files:
					logger.info("+ '%s' => '%s'", source, destination)
					archive_file.write(source, destination)
			shutil.move(artifact_path + ".zip.tmp", artifact_path + ".zip")


	def verify(self, path_in_repository, artifact_name, simulate):
		logger.info("Verifying artifact '%s'", artifact_name)

		artifact_path = os.path.join(self.local_path, path_in_repository, artifact_name)
		logger.info("Reading '%s'", artifact_path + ".zip")

		if not simulate:
			with zipfile.ZipFile(artifact_path + ".zip", 'r') as archive_file:
				if archive_file.testzip():
					raise RuntimeError('Artifact package is corrupted')


	def upload(self, path_in_repository, artifact_name, overwrite, simulate):
		self.server_client.upload(self.local_path, self.project_identifier, path_in_repository, artifact_name, ".zip", overwrite, simulate)


	def download(self, path_in_repository, artifact_name, simulate):
		self.server_client.download(self.local_path, self.project_identifier, path_in_repository, artifact_name, ".zip", simulate)


	def install(self, path_in_repository, artifact_name, installation_directory, simulate):
		logger.info("Installing artifact '%s' to '%s'", artifact_name, installation_directory)

		artifact_path = os.path.join(self.local_path, path_in_repository, artifact_name)
		extraction_directory = os.path.join(self.local_path, ".extracting")

		if not simulate and os.path.isdir(extraction_directory):
			shutil.rmtree(extraction_directory)

		print("")

		logger.info("Extracting files to '%s'", extraction_directory)
		with zipfile.ZipFile(artifact_path + ".zip", "r") as artifact_file:
			artifact_files = artifact_file.namelist()
			for source in artifact_files:
				destination = os.path.join(extraction_directory, source).replace("\\", "/")
				logger.info("+ '%s' => '%s'", source, destination)
				if not simulate:
					artifact_file.extract(source, extraction_directory)

		print("")

		logger.info("Moving files files to '%s'", installation_directory)
		for file_path in artifact_files:
			source = os.path.join(extraction_directory, file_path).replace("\\", "/")
			destination = os.path.join(installation_directory, file_path).replace("\\", "/")
			logger.info("+ '%s' => '%s'", source, destination)
			if not simulate:
				os.makedirs(os.path.dirname(destination), exist_ok = True)
				shutil.move(source, destination)

		if not simulate:
			shutil.rmtree(extraction_directory)


	def delete_remote(self, path_in_repository, artifact_name, simulate):
		self.server_client.delete(self.project_identifier, path_in_repository, artifact_name, ".zip", simulate)
