API
===

The harvester comes with an API to get and annotate learning materials.


Login
-----

It's possible to send the following header to the backend:

```bash
Authorization: Token <api-token>
```

If the API token is valid then your request will be done on behalf of the user that the token belongs to.
In general all API endpoints are open, but when storing data the data gets stored under the user.
This makes it possible to attribute input to a particular user.

API tokens are valid indefinitely until they get deleted in the administration interface.
You can create/retrieve tokens through the API by using the following request:

```bash
POST /api/v1/auth/token/

{
    "username": <username>,
    "password": <password>
}
```


Read learning materials
-----------------------

To read which learning materials are in the database it is first necessary to know which ``Freezes`` exist.
A ``Freeze`` is a moment in time where certain learning materials were processed.
You can list all available ``Freezes`` by calling:

```bash
GET /api/v1/freeze/
```

This returns a list of all ``Freezes``. For a single ``Freeze`` you can get all existing ``content``
and ``annotations`` by calling:

```bash
GET /api/v1/freeze/<freeze-id>/
```

This is what a freeze object looks like:

```bash
{
    "id": 13,
    "name": "alpha",
    "created_at": "2019-05-09T11:47:10.898999Z",
    "modified_at": "2019-05-23T11:04:34.465521Z",
    "schema": null,
    "referee": "id",
    "identifier": null,
    "indices": [
        {
            "id": 1,
            "name": "alpha",
            "language": "nl",
            "remote_name": "alpha-nl-1"
        }
    ]
}
```

Most of this can safely be ignored, but what is important is the name.
People can recognize and select ``Freezes`` by name.
Another important aspect are the indices. These are Elastic Search indices.
When people search in a particular ``Freeze``
the Elastic Search query should be
a [multi-index query](https://www.elastic.co/guide/en/elasticsearch/reference/6.3/multi-index.html)
using all ``remote_name`` from the ``Freeze`` as index names.


Annotate learning materials
---------------------------

To add ``Annotations`` to learning materials you first need to find a ``Freeze`` in the ``Freezes`` list.
Read more under [Read learning materials](#read-learning-materials).
``Annotations`` persist across ``Freezes``, but you still need to specify one ``Freeze``.
When you GET annotations then ``Documents`` get randomly drawn from the specified ``Freeze``.

To get a list of random Documents that lack a ``language`` annotation you can call:

```bash
GET /api/v1/freeze/<freeze-id>/annotate/language/
```

You can replace the ``language`` path segment to get random ``Documents`` that lack the ``Annotation`` you specify.
That particular segment path will be the name of any created ``Annotations``

To actually create an ``Annotation`` you can make the following call:

```bash
POST /api/v1/freeze/<freeze-id>/annotate/language/

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


Recording queries
-----------------

Recording a ``Query`` is a bit more involved than creating a ``Annotation``,
but it is a much better way to store search query annotations.

The basic process is the same. You still need to know the ``Freeze`` to create or update a ``Query``.
Once you know the ``Freeze`` and you are logged in you can make a request like this:


```bash
POST /api/v1/search/query/

{
    "query": <main-query>,
    "rankings": [
        {
            "subquery": <sub-query>,
            "ranking": {
                <document-reference>: <rating>
            },
            "freeze": <freeze-id>
        }
    ]
}
```

If you want to update a query you can make the same post with different ranking data.
A user will only change his/her own rankings.
So it's possible for a ``Query`` to exists without rankings for a particular user.
However if you want to update a ``Query`` the user needs to provide at least one ranking for the main query.

Getting all rankings that a user has ever made is easy:

```bash
GET /api/v1/search/query/
```

Once you have the document references you can use them to query the search documents from Elastic Search.
There is for instance their [multi get](https://www.elastic.co/guide/en/elasticsearch/reference/6.3/docs-multi-get.html) API call.
The references are equal to the ``_id`` properties in Elastic Search.

Notice that if you want to delete a ranking or an entire ``Query`` you'll need to login to the administration.
The ``Queries`` can be found at: ``/admin/search/query/``
