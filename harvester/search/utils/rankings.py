import os
import json
from itertools import chain
from collections import OrderedDict

from datagrowth import settings as datagrowth_settings


def yield_query_rankings():
    with open(os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, "queries", "queries-en.json")) as en_queries_file:
        en_queries = json.load(en_queries_file)
    with open(os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, "queries", "queries-nl.json")) as nl_queries_file:
        nl_queries = json.load(nl_queries_file)

    for query_info in chain(nl_queries, en_queries):
        query = query_info["queries"][0]
        sorted_items = sorted(
            ((item["hash"], item["rating"],) for item in query_info["items"]),
            key=lambda item: item[1],
            reverse=True  # TODO: check if higher is indeed better, it's required for the metric it seems
        )
        ranking = OrderedDict(sorted_items)
        yield query, ranking
