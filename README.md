Project Open Leermaterialen
===========================

A repo meant to scrape, extract and publish education materials.

Prerequisites
-------------

This project uses ``Docker`` and ``docker-compose``.
Make sure they are installed on your system before installing the project.
The project also uses the Tika CLI. It currently works with the ``tika-app-1.19.1.jar`` JAR file.
Place this file after cloning in the ``harvester/datagrowth/resources/shell/bin`` directory.


Installation
------------

Copy the ``.env.development`` file to ``.env`` and update the variable values to fit your system.
When you're running the project locally it is ok to keep the values as is.

Inside of the root directory of this repo run the following command:

```bash
bash start.sh
```

This will build and run the software in the background. 
The exact same command gets used when deploying a new version of the harvester to production.

When running the project for the first time one more command is needed to complete the installation process.

```bash
docker-compose run harvester setup.sh
``` 

Now the administrator interface and API are available under:

```bash
http://localhost:8000/admin/
http://localhost:8000/api/v1/
```

When developing it can be useful to see the uWSGI output.
To run the project locally with visible output you can simply run:

```bash
docker-compose up
```


Documentation
-------------

How to harvest learning materials is described in detail in the [harvester documentation](harvester/HARVEST.md). 

If you want to know more about the available API please read the [API documentation](harvester/API.md)


Datagrowth
----------

Datagrowth is a set of open source tools that helps to gather and organise data through Django.
I've included the sources to this repo directly, but I mostly copy pasted it from another repo.
When Datagrowth gets released as a package we should consider installing it as a dependency 
rather than using the copied sources.
