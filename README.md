Project Open Leermaterialen
===========================

A repo meant to scrape, extract and publish education materials.

Prerequisites
-------------

This project uses ``Docker`` and ``docker-compose``. Make sure they are installed on your system before installing the project.


Getting started
---------------

Copy the ``.env.development`` file to ``.env`` and update the variable values to fit your system.
When you're running the project locally you'll only need to provide your Elastic Search credentials.

Inside of the root directory of this repo run the following command:

```bash
bash start.sh
```

This will build and run the backend software in the background.
The exact same command gets used when deploying a new version of the harvester to production.

After this basic installation you'll need to load the data.
Get a Postgres dump file and load it with the following command from the root directory:

```bash
make import-db backup=<dump-file>
```

When running the project for the first time one more command is needed to complete the installation process.
This command allows you to create your own local superuser for the administration interface.

```bash
docker-compose run harvester setup.sh
``` 

Now the administrator interface and API are available under:

```bash
http://localhost:8000/admin/
http://localhost:8000/api/v1/
```

Don't forget to stop your Docker containers when you're done working:

```bash
docker-compose down
```

When developing it can be useful to see the uWSGI output.
To run the project locally with visible output you can simply run:

```bash
docker-compose up
```


Documentation
-------------

How to harvest learning materials is described in detail in the [harvester documentation](harvester/HARVEST.md). 

If you want to know more about the available API please read the [API documentation](harvester/API.md).

You can read more about Elastic Search in the [Elastic Search documentation](elasticsearch/readme.md).


Datagrowth
----------

Datagrowth is a set of open source tools that helps to gather and organise data through Django.
I've included the sources to this repo directly, but I mostly copy pasted it from another repo.
When Datagrowth gets released as a package we should consider installing it as a dependency 
rather than using the copied sources.
