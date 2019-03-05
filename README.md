Project Open Leermaterialen
===========================

A repo meant to scrape, extract and publish education materials.

Prerequisites
-------------

This project uses ``Docker`` and ``docker-compose``. Make sure they are installed on your system before installing the project.


Installation
------------

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
