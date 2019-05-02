API
===

The harvester comes with an API to get and annotate learning materials.

Read learning materials
-----------------------

To read which learning materials are in the database it is first necessary to know which ``Freezes`` exist.
A ``Freeze`` is a moment in time where certain learning materials were processed.
You can list all available ``Freezes`` by calling:

```bash
GET https://ltidev.surfpol.nl/api/v1/freeze/
```

This returns a list of all ``Freezes``. For a single ``Freeze`` you can get all existing ``content``
and ``annotations`` by calling:

```bash
GET https://ltidev.surfpol.nl/api/v1/freeze/<freeze-id>/
```


Annotate learning materials
---------------------------

To add ``Annotations`` to learning materials you first need to find a ``Freeze`` in the ``Freezes`` list.
Read more under [Read learning materials](#read-learning-materials).
``Annotations`` persist across ``Freezes``, but you still need to specify one ``Freeze``
where random ``Documents`` gets drawn from.

To get a list of random Documents that lack a ``language`` annotation you can call:

```bash
GET https://ltidev.surfpol.nl/api/v1/freeze/<freeze-id>/annotate/language/
```

You can replace the ``language`` path segment to get random ``Documents`` that lack the ``Annotation`` you specify.
That particular segment path will be the name of any created ``Annotations``

To actually create an ``Annotation`` you can make the following call:

```bash
POST https://ltidev.surfpol.nl/api/v1/freeze/<freeze-id>/annotate/language/

{
    "reference": <document-reference>,
    "annotations": {
        "language": "en",
        "text_length": 0
    }
}
```

This will create two ``Annotations``. One with the name ``language`` and another named ``text_length``.
Both will be attached to the document reference.
As long as this reference does not change between ``Freezes`` the ``Annotations`` persist.
Only the ``language`` ``Annotation`` is required, because that ``Annotation`` is specified in the request path.
Both string and numbers will be excepted as ``Annotation`` values.
