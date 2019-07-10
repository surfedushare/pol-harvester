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
    "47400bd9de5920a96b461433734ed5379a53da3d": 0.5079779518421816,
    "ea3cc3dbf6b9309b3f35f102bf0e3094ee85bba1": 0.47194719471947194,
    "3fb1ec3dfb37004ce6e5d0e3a4c66962ab7f1836": 0.7694877505567929,
    "063b9b2562578274d47579025a9cf15483bf5732": 0.5327868852459017,
    "f3efd1a94f3212de77a450f3c5aaf4ab38fc97c8": 0.9839743589743589,
    "3d745e7adde31354c12f15c55f2e2a805bb6de3b": 0.9823788546255506,
    "6f6ae1d8cd6a2cc541620ded919f9f317466cdd5": 0.5894495412844036
}

jargon = {
    "47400bd9de5920a96b461433734ed5379a53da3d": 0.4798375398897592,
    "ea3cc3dbf6b9309b3f35f102bf0e3094ee85bba1": 0.45654565456545654,
    "3fb1ec3dfb37004ce6e5d0e3a4c66962ab7f1836": 0.799554565701559,
    "063b9b2562578274d47579025a9cf15483bf5732": 0.4979508196721312,
    "f3efd1a94f3212de77a450f3c5aaf4ab38fc97c8": 0.17307692307692307,
    "3d745e7adde31354c12f15c55f2e2a805bb6de3b": 0.3039647577092511,
    "6f6ae1d8cd6a2cc541620ded919f9f317466cdd5": 0.5290519877675841
}
``` 
