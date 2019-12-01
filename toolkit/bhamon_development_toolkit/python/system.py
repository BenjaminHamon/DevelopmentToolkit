import logging
import os
import platform
import subprocess


logger = logging.getLogger("Python")


def setup_virtual_environment(python_system_executable, target_directory, simulate):
	setup_venv_command = [ python_system_executable, "-m", "venv", target_directory ]
	logger.info("+ %s", " ".join(setup_venv_command))
	if not simulate:
		subprocess.check_call(setup_venv_command)

	if platform.system() == "Linux" and not os.path.exists(os.path.join(target_directory, "scripts")):
		if not simulate:
			os.symlink("bin", os.path.join(target_directory, "scripts"))

	install_pip_command = [ os.path.join(target_directory, "scripts", "python"), "-m", "pip", "install", "--upgrade", "pip" ]
	logger.info("+ %s", " ".join(install_pip_command))
	if not simulate:
		subprocess.check_call(install_pip_command)


def install_packages(python_executable, python_package_repository, package_collection, simulate):
	install_command = [ python_executable, "-m", "pip", "install", "--upgrade" ]
	install_command += [ "--extra-index", python_package_repository ] if python_package_repository is not None else []

	for package in package_collection:
		install_command += [ "--editable", package ] if os.path.isdir(package) else [ package ]

	logger.info("+ %s", " ".join(("'" + x + "'") if " " in x else x for x in install_command))
	if not simulate:
		subprocess.check_call(install_command)
