ANALYSE
=======

There are some commands available that will analyse how a part of the system is functioning.
This documentation describes how to run these commands.


Video transcription analysis
----------------------------

Video transcripts can be compared to annotations.
The annotations are assumed to be created through the [annotation API](API.md).

By running the following command you will compare all transcripts in a freeze with the available annotations.
The comparison will be expressed in Word Error Rate (WER).
Annotations or transcripts that have a falsy value will be silently ignored.

```bash
./manage.py analyse_transcription_errors --freeze <freeze-name>
```

The command should create a histogram of errors and report on totals and averages.
Alternatively you can print the WER's of a subset called "hbovpk".
This subset is transcribed with a special KaldiNL graph that contains jargon words for the nursery domain.
To run an analysis on this subset specify hbovpk at the end like:

```bash
./manage.py analyse_transcription_errors --freeze <freeze-name> --hbovpk
```

This first prints the WER's from the freeze and after that from the special HBOVPK transcriptions.
These transcriptions can be found in the KaldiNLResource table. 
The references for the annotations are set in the config column of this table.

At the time of writing the alpha freeze was the latest and the output of th HBOVPK WER command was:

```python
original = {
    "47400bd9de5920a96b461433734ed5379a53da3d": 0.5059334298118668,
    "ea3cc3dbf6b9309b3f35f102bf0e3094ee85bba1": 0.4712892741061755,
    "3fb1ec3dfb37004ce6e5d0e3a4c66962ab7f1836": 0.7751351351351351,
    "063b9b2562578274d47579025a9cf15483bf5732": 0.5460060667340748,
    "f3efd1a94f3212de77a450f3c5aaf4ab38fc97c8": 0.9839228295819936,
    "3d745e7adde31354c12f15c55f2e2a805bb6de3b": 0.9824304538799414,
    "6f6ae1d8cd6a2cc541620ded919f9f317466cdd5": 0.5993907083015994
}

jargon = {
     "47400bd9de5920a96b461433734ed5379a53da3d": 0.4784370477568741,
     "ea3cc3dbf6b9309b3f35f102bf0e3094ee85bba1": 0.4539544962080173,
     "3fb1ec3dfb37004ce6e5d0e3a4c66962ab7f1836": 0.8140540540540541,
     "063b9b2562578274d47579025a9cf15483bf5732": 0.5096056622851365,
     "f3efd1a94f3212de77a450f3c5aaf4ab38fc97c8": 0.16720257234726688,
     "3d745e7adde31354c12f15c55f2e2a805bb6de3b": 0.30161054172767204,
     "6f6ae1d8cd6a2cc541620ded919f9f317466cdd5": 0.5354150799695354
}
``` 


Ranked query analysis
---------------------

There are also search query annotations that you can compare to search results.
These annotations are made through the ``rateapp``.

Elastic Search provides an experimental API interface to compare search query annotations with search results.
By running the following command you compare search query annotations with different search query configurations.
The results of the comparison get dumped to a directory. Other tools exist to visualize the outcomes.

```bash
./manage.py create_es_ranked_queries --freeze <freeze-name> --username <annotator-username>
```

This results into a dump file per metric inside of the folder ``data/elastic/<freeze-name>/<date-today>/``.
Notice that for each user you run the command for you'll get different files with results for that user.

By specifying ``--fields`` you overwrite which fields are taken into account when creating different query configurations.
By specifying ``--results-count`` you specify how many results should be taken into account for the analysis.
Be careful to run the same command with different fields and/or results-count options. They overwrite any existing results.


Google search analysis
----------------------

You can use a custom Google Search engine and see if the query annotations line up with those Google results.
Run the following command to start the analysis:

```bash
./manage.py analyse_google_search
```
