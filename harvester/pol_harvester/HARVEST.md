Harvesting commands
===================

I've made some management commands that together fully harvest repositories or other repositories like Edurep.
A harvest results in a ``Freeze``, which is a snapshot of data from in theory various sources.
Currently we only support Edurep as a source.


#### 1.) Create a new Freeze

If you want to create a completely new snapshot of Edurep you first need to create a ``Freeze`` in the admin section.
Visit the following URL and create a ``Freeze``:

```bash
/admin/pol_harvester/freeze/add/
```

We use the Greek alphabet to name freezes, but this is a convention only.
As ``referee`` you should specify ``id``. This means that a ``Document`` added to the ``Freeze``
will have its ``reference`` attribute set to the value of the ``id`` property.


#### 2.) Add harvest sources

Currently a ``Freeze`` can only contain harvests from Edurep.
You need to specify which sources you want to include in the ``Freeze``.
For each source you need to specify from which date you want to start to harvest it.
By default this is 01-01-1970.

You can create new sources as well as select sources from a previous ``Freeze``.
When you create a new ``EdurepSource`` you need to specify a ``name`` and ``collection_name``.
The ``name`` is only used in the admin interface.
The ``collection_name`` will be used as a name for the ``Collection`` where documents for the harvest will get stored.
It also indicates the Edurep set that you want to harvest through OAI-PMH.


#### 3.) Run harvest management commands

You need to run the following harvest commands to gather data from Edurep and the URL's that Edurep points to.
The order of the commands is important. The system will not proceed to step B if step A hasn't been completed.

##### A.) Metadata

First we'll download metadata from Edurep to see which learning materials are available

```bash
./manage.py harvest_edurep_seeds -f <your-freeze-name>
```

##### B.) Basic source files

Then we'll download basic files like HTML and PDF files.
These files will go through Tika to extract texts from them.

```bash
./manage.py harvest_edurep_basic -f <your-freeze-name>
```

##### C.) Video files (optional)

You can choose to download and transcribe the video content with this command:

```bash
./manage.py harvest_edurep_video -f <your-freeze-name>
```

Or if you wish to skip this step you can run a dummy video harvest with:

```bash
./manage.py harvest_edurep_video -f <your-freeze-name> --dummy
```

Running a dummy harvest will skip the video, but allows you to continue the pipeline.


#### 4.) Aggregate data in a freeze

So far these commands have executed various parts of a pipeline, but nothing has been combined yet.
We aggregate the results of the pipeline in a ``Collection``, which is a set of ``Documents``.
These ``Documents`` get extracted from an ``Arrangement``.
An ``Arrangement`` is a learning materials as exposed in the search portal.
If a HTML page contains text and a video than the text and video are ``Documents`` belonging to the same ``Arrangements``.
You can think of ``Arrangements`` as unique URL's that point to learning materials.
The ``Collections`` of ``Documents`` get stored by Django in a no-SQL fashion to allow dynamic queries.
There is a ``Collection`` for every learning material source, which is the same as a OAI-PMH set.
All these different sources together form a ``Freeze``.
That way a ``Freeze`` holds all ``Documents`` from all ``Collections`` for a certain pipeline version.
``Documents`` are possibly grouped in ``Arrangements``. There is at least one ``Document`` for every ``Arrangment``
and no ``Documents`` without one.

By running the commands below we store the data from the previous steps into the database.

```bash
./manage.py freeze_edurep --freeze <your-freeze-name>
```

Updating a Freeze
-----------------

If you want to update existing ``Arrangements`` and/or ``Documents`` from an existing ``Freeze``
without going through the entire process from the start.
It's possible to execute a delta update. Simply repeat the steps from step 3 onwards.
Through the OAI-PMH protocol the harvester will only retrieve materials that are newer than your last harvest.



Working with Library for Learning
---------------------------------

The Library for Learning materials take a slightly different approach.
The video transcripts and metadata for this collection comes directly in a XML file from Wageningen.
By specifying a freeze, the name of the collection ("wur" traditionally)
and an input XML file the L4L data gets added to a ``Freeze``.

```bash
./manage.py freeze_library_4_learning --freeze <your-freeze-name> --collection <source-name> --input <data-file>
```


Putting data in Elastic Search
------------------------------

Once the data is harvested it is necessary to create an index on the Elastic Search instance.
You can do this by running the following command:

```bash
./manage.py push_es_index --freeze <your-freeze-name>
```

After this command the Elastic Search index should show up in the administration interface under
``/admin/search/elasticindex/``.

There is an optional flag ``--recreate`` that you can add to the command when an index already exists on the remote.
This will delete any existing indices on the remote before creating a new one.
