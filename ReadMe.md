<!-- cspell:words epub pylint pytest venv -->

# Development Toolkit



## Overview

Development Toolkit is a library of modules intended to help with development task automation, and more generally with writing scripts for software development. This notably includes building and packaging applications, running tests, software delivery, interacting with processes, communicating with web services, managing configuration files, parsing logs, managing artifacts, etc.

See the [Automation](Documentation/Automation.md) documentation page for more information on the topic.

This project is free and open source software. See [About](About.md) for more information.



## Scope

This toolkit is about providing interfaces for common development tools as well as utilities for simple, commonplace operations. It does not replace compilers, editors, test runners, etc., but provides means to unify their interfaces and aggregate their results. It also helps with the shortcomings of tools when they cannot be addressed directly.



## Development

The project is developed using Python and supports the usual workflows with `pip`, `pylint` and `pytest`. It is highly recommended to use a Python virtual environment.

Additionally, there are commands to automate development related tasks, as can be found under [Automation](Automation). Use the `Automation/Setup/setup.py` script for a quick setup. Following that, the commands will be available through `.venv-automation/scripts/automation`, or `automation` directly after activating the `venv-automation` virtual environment. This executable corresponds to the `Automation/Scripts/automation_scripts/run_command.py` script. Use the `--help` option for information, and the `--simulate` option if you wish to check a command's behavior before actually running it.
