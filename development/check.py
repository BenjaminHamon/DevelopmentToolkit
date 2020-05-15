import logging
import os
import sys

sys.path.insert(0, os.path.join(sys.path[0], ".."))

import development.configuration # pylint: disable = wrong-import-position
import development.environment # pylint: disable = wrong-import-position


logger = logging.getLogger("Main")


def main():
	with development.environment.execute_in_workspace(__file__):
		environment_instance = development.environment.load_environment()
		configuration_instance = development.configuration.load_configuration(environment_instance) # pylint: disable = unused-variable
		development.environment.configure_logging(environment_instance, None)

		global_status = { "success": True }

		check_commands(global_status)

	if not global_status["success"]:
		raise RuntimeError("Check found issues")


def check_commands(global_status):
	command_list = development.configuration.load_commands()

	for command in command_list:
		if "exception" in command:
			global_status["success"] = False
			logger.error("Command '%s' is unavailable", command["module_name"], exc_info = command["exception"])
			print("")


if __name__ == "__main__":
	main()
