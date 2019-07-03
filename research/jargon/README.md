Adding jargon to Kaldi NL
=========================

This directory brings together some code that we use to add vocabulairy to Kaldi NL.
It is mostly a documentation of the steps we took to learn higher education nursery jargon.
The guide is very basic and not meant to be complete.
For a more thorough guide checkout: [Artificial Industry docs on Kaldi NL jargon](https://docs.google.com/document/d/1Zq6pZnFX2T5f17zRYALYcP0P1KJ3jBJHgD9AIEaM848/edit#heading=h.oc4yz21n922g).


Selecting jargon
----------------

We looked at 7 silver standard transcripts and manually selected words that we felt could be considered jargon.
Here are the references for these transcripts:

* 063b9b2562578274d47579025a9cf15483bf5732
* 3d745e7adde31354c12f15c55f2e2a805bb6de3b
* 3fb1ec3dfb37004ce6e5d0e3a4c66962ab7f1836
* 47400bd9de5920a96b461433734ed5379a53da3d
* 6f6ae1d8cd6a2cc541620ded919f9f317466cdd5
* ea3cc3dbf6b9309b3f35f102bf0e3094ee85bba1
* f3efd1a94f3212de77a450f3c5aaf4ab38fc97c8

We merged all resulting vocabularies 
and checked whether the words really did not occur already in the Kaldi NL vocabulairy.
We identified 29 terms that Kaldi NL does not yet recognize.
You can find these terms in the [HBOVPK vocabulairy file](vocabularies/hbovpk/vocabulairy.txt).

#### Additional jargon

We identified some jargon that is not present in any of the transcripts by listening to additional videos.
That list is present in the [extra HBOVPK vocabulairy file](vocabularies/hbovpk/vocabulairy-extra.txt).


#### Errors

There are words that Kaldi NL has in its dictionary, but which were misunderstood.
One possible reason for this is that the language model is not suitable for the domain we're listening to.
For instance "wezens" seems to have president over "weefsels", which for a medical application is probably wrong.
Re-training the language model may help, but is out of scope for this research.
A complete list of errors can be found in the [HBOVPK error file](vocabularies/hbovpk/vocabulairy-errors.txt).


Transforming jargon to phonemes
-------------------------------


