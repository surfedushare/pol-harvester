Harvesting commands
===================

I've made some management commands that harvest various sources.
Later these commands can be chained to a proper pipeline.

#### 1.) Downloading data

There are a few ways to get raw data, where the content harvesting can start from:
- As a search query
- As a XML dump (in a Library 4 Learning format)

If you got the data as a dump proceed to step 2. If you only have a Edurep query you can download the raw metadata with:

```bash
./manage.py harvest_edurep_api --query <your-query>
```

Currently we're using the following commands to get the data from Edurep:

```bash
./manage.py harvest_edurep_api --query hbovpk
./manage.py harvest_edurep_api --query meta.repository.id=Leraar24_Publicaties
./manage.py harvest_edurep_api --query meta.repository.id=wikiwijsmaken+AND+lom.educational.context=HBO
./manage.py harvest_edurep_api --query meta.repository.id=wikiwijsmaken+AND+lom.educational.context=WO
```

#### 2.) Extracting relevant data

We "extract" data from raw data to bring all data into the same format and to discard data we do not need.
How this extraction is done depends slightly on your initial raw data.
Use one of the commands below:

```bash
# When using Edurep search queries
./manage.py extract_edurep_api --query <your-query> --output <your-data-file>

# When reading Library 4 Learning XML dumps
./manage.py extract_library_4_learning_xml --input <the-XML-dump-file> --output <your-data-file>

```

Notice how all these commands create a similar output file that we'll call the ```data file``` from now on.

#### 3.A) Download content

Edurep only harvests meta data. To get the content of the learning materials you can run the following commands.
These commands internally use TIKA to extract texts from files.

```bash
./manage.py download_edurep --input <data-file>
./manage.py extract_text_edurep_files --input <data-file>
```

This will put the content in files on your harddisk under the ```media``` directory. 
You can find all downloaded content with paths as well as metadata from Tika in the database.

#### 3.B) Download and transcribe video

Some of the Edurep content consists of video. We need to download this content separately using the commands below.
Internally these commands use YoutubeDL and Kaldi to download the audio and transcribe to text.

```bash
./manage.py download_edurep_video --input <data-file>
./manage.py transcribe_edurep_video --input <data-file>
```

As with step 3.A all files will be stored under ```media``` while the paths to these files 
and possible error messages that occured will reside in the database.
Note that only .wav files get stored permanently.


#### 3.C) Download and extract IMS Content Packages

Other content consists of content packages as defined by IMS.
You can download and extract these with the following commands:

```bash
./manage.py download_edurep_imscp --input <data-file>
./manage.py extract_text_edurep_imscp --input <data-file>
```

This places the package download and extracted files under ```media```. It will also process the extracted files with Tika.
Errors in this process are to be found in the database.

#### 4.) Aggregate data in a freeze

So far these commands have executed various parts of a pipeline, but nothing has been combined yet.
We aggregate the results of the pipeline in a ``Collection``, which is a set of ``Documents``.
These ``Documents`` get extracted from a ``Arrangement``.
An ``Arrangement`` is a set of learning materials that belong together.
If a HTML page contains text and a video than the text and video are ``Documents`` belonging to the same ``Arrangements``.
You can think of ``Arrangements`` as unique URL's that point to learning materials.
The ``Collections`` of ``Documents`` get stored by Django in a no-SQL fashion to allow dynamic queries.
There is a ``Collection`` for every learning material repository.
All these different repositories together form a ``Freeze``.
That way a ``Freeze`` holds all ``Documents`` from all ``Collections`` for a certain pipeline version.
``Documents`` are possibly grouped in ``Arrangements``. There is at least one ``Document`` for every ``Arrangment``
and no ``Documents`` without one.

By running the commands below we store the data from the previous steps into the database.

```bash
./manage.py freeze_edurep --freeze <pipeline-name> --collection <source-name> --input <data-file>
./manage.py freeze_library_4_learning --freeze <pipeline-name> --collection <source-name> --input <data-file>
./manage.py freeze_surfshare --freeze <pipeline-name> --collection <source-name> --input <data-file>
```
