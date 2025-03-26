# Automation

This page is an overview for the topic of automation, as referring to the various tasks associated with software development. This notably includes building and packaging applications, running tests, software delivery, interacting with processes, communicating with web services, managing configuration files, parsing logs, managing artifacts, etc.



## Objective

The objective of automation is to provide an easy-to-use, standardized interface for all the development tasks of a project, destined to be used both by the project contributors and in automated workflows (for example, continuous integration and delivery). Automation describes and implements each task so that it can be performed by any person through more or less of a single button press. It also ensures each task can be versioned, reviewed, and logged.



# Reasoning

Here are a few use cases where setting up automation can be useful:

- You perform a task by going through a number of manual operations. Automation makes it all a single action, decreasing the risk for mistakes and the amount of knowledge required.
- You perform a critical and uncommon task such as a delivery. Automation makes it a simpler, standardized process. It makes it safer and simpler, through ensuring every step is performed as expected.
- A tool you're using does not provide some feature. Automation performs any extra steps you need for each task.
- A tool you're using has limited configuration support. Automation makes and undoes configuration changes before and after executing a tool.
- A tool you're using generates results the format of which you're unhappy with. Automation modifies and cleans files as needed.
- A tool you're using generates logs that are hard to read. Automation translates logs to a nicer format and extracts whatever information you're looking for.
- You implement extra operations in whatever editor you're using. Automation makes it independent of the editor.



Automation documents and standardizes workflows. It makes them simpler and safer, often faster. It decreases the risk for mistakes and the amount of knowledge required to perform a task. Furthermore, it extends the capabilities of whatever tools you're using and reduces your dependency on a single development environment.



**Automation documents and standardizes workflows.**

Your workflow for a given task might exists, it might even have a written guide. Automating it means documenting it directly, through code and logging, and ensuring it is standardized, meaning it goes through every step every time.



**Automation makes workflows simpler and safer.**

Automating a workflow means reducing the number of manual operations you will be performing, this makes the task easier to understand and decreases the risk for mistakes, thus making each execution simpler and safer, both for every day operations and for people training.



**Automation often makes workflows faster.**

Automating a workflow reduces the amount of human input and allows internal optimization, which may result in a faster process overall. However, speed is not a primary goal of automation, only a potential bonus.



**Automation extends the capabilities of whatever tools you're using and reduces your dependency on a single development environment.**

It is common for development environments to provide means to perform extra actions, but it has drawbacks: the software capabilities may limit you, in means and configuration, and it places unrelated matters between the constraints of that environment. Using automation for this gives you more flexibility for what you want to accomplish and for changing tools and environment in the future.
