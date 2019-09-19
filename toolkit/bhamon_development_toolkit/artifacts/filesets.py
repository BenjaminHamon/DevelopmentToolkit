import copy
import filecmp
import glob
import logging
import os


logger = logging.getLogger("Artifact")


def list_files(artifact, fileset_getter, parameters):
	artifact_files = []

	for fileset_options in artifact["filesets"]:
		fileset = fileset_getter(fileset_options["identifier"])
		fileset_parameters = copy.deepcopy(fileset_options.get("parameters", {}))
		fileset_parameters.update(parameters)

		artifact_files += load_fileset(fileset, fileset_parameters)

	artifact_files.sort()

	return artifact_files


def map_files(artifact, fileset_getter, parameters):
	artifact_files = []

	for fileset_options in artifact["filesets"]:
		fileset = fileset_getter(fileset_options["identifier"])
		fileset_parameters = copy.deepcopy(fileset_options.get("parameters", {}))
		fileset_parameters.update(parameters)

		path_in_workspace = fileset["path_in_workspace"].format(**fileset_parameters)
		for source in load_fileset(fileset, fileset_parameters):
			destination = source
			if "path_in_archive" in fileset_options:
				destination = os.path.join(fileset_options["path_in_archive"], os.path.relpath(source, path_in_workspace))
			artifact_files.append((source, destination.replace("\\", "/")))

	artifact_files = merge_mappings(artifact_files)

	artifact_files.sort()

	return artifact_files


def merge_mappings(artifact_files):
	merged_files = []
	has_conflicts = False

	for destination in set(dst for src, dst in artifact_files):
		source_collection = [ src for src, dst in artifact_files if dst == destination ]
		for source in source_collection[1:]:
			if not filecmp.cmp(source_collection[0], source):
				has_conflicts = True
				logger.error("Mapping conflict: %s, %s => %s", source_collection[0], source, destination)
		merged_files.append((source_collection[0], destination))

	if has_conflicts:
		raise ValueError("Artifact mapper has conflicts")

	merged_files.sort()

	return merged_files


def check_files(artifact_files):
	has_issues = False

	for file_path in artifact_files:
		if not os.path.exists(file_path):
			has_issues = True
			logger.error("Missing file: %s", file_path)

	if has_issues:
		raise ValueError("Artifact files have issues")


def load_fileset(fileset, parameters):
	matched_files = []
	path_in_workspace = fileset["path_in_workspace"].format(**parameters)

	for file_function in fileset.get("file_functions", []):
		matched_files += file_function(path_in_workspace, parameters)
	for file_pattern in fileset.get("file_patterns", []):
		matched_files += glob.glob(os.path.join(path_in_workspace, file_pattern.format(**parameters)), recursive = True)

	selected_files = []
	for file_path in matched_files:
		file_path = file_path.replace("\\", "/")
		if not os.path.isdir(file_path):
			selected_files.append(file_path)

	selected_files.sort()

	return selected_files
