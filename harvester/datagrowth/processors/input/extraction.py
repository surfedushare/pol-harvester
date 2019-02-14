from copy import copy, deepcopy

from datagrowth.configuration import ConfigurationProperty, DEFAULT_CONFIGURATION
from datagrowth.exceptions import DGNoContent


def reach(path, data):
    """
    Reach takes a data structure and a path. It will return the value belonging to the path,
    the value under a key containing dots mistaken for a path or None if nothing can be found.

    Paths are essentially multiple keys or indexes separated by '.'
    Each part of a path is another level in the structure given.
    For instance with a structure like
    {
        "test": {"test": "second level test"},
        "list of tests": ["test0","test1","test2"]
    }
    "test.test" as path would return "second level test"
    while "test.1" as path would return "test1"
    """
    if path and path.startswith("$"):  # TODO: fix now that legacy is gone
        if len(path) > 1:
            path = path[2:]
        else:
            path = None

    # First we check whether we really get a structure we can use
    if path is None:
        return data
    if not isinstance(data, (dict, list, tuple)):
        raise TypeError("Reach needs dict, list or tuple as input, got {} instead".format(type(data)))

    # We make a copy of the input for later reference
    root = deepcopy(data)

    # We split the path and see how far we get with using it as key/index
    try:
        for part in path.split('.'):
            if part.isdigit():
                data = data[int(part)]
            else:
                data = data[part]
        else:
            return data

    except (IndexError, KeyError, TypeError):
        pass

    # We try the path as key/index or return None.
    path = int(path) if path.isdigit() else path
    return root[path] if path in root else None


class ExtractProcessor(object):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=["_objective"],
        namespace="extract_processor"
    )

    def __init__(self, config):
        assert isinstance(config, dict), "Processor expects to always get a configuration."
        self.config = config
        self._at = None
        self._context = {}
        self._objective = {}
        if "_objective" in config or "objective" in config:
            self.load_objective(self.config.objective)

    def load_objective(self, objective):
        assert isinstance(objective, dict), "An objective should be a dict."
        for key, value in objective.items():
            if key == "@":
                self._at = value
            elif key.startswith("#"):
                self._context.update({key[1:]: value})
            else:
                self._objective.update({key: value})
        assert self._objective or self._context, "No objectives loaded from objective {}".format(objective)
        if self._objective:
            assert self._at, \
                "ExtractProcessor did not load elements to start with from its objective {}. " \
                "Make sure that '@' is specified".format(objective)

    def pass_resource_through(self, resource):
        mime_type, data = resource.content
        return data

    def extract_from_resource(self, resource):
        return self.extract(*resource.content)

    def extract(self, content_type, data):
        assert self.config.objective, \
            "ExtractProcessor.extract expects an objective to extract in the configuration."
        if content_type is None:
            return []
        content_type_method = content_type.replace("/", "_")
        method = getattr(self, content_type_method, None)
        if method is not None:
            return method(data)
        else:
            raise TypeError("Extract processor does not support content_type {}".format(content_type))

    def application_json(self, data):
        context = {}
        for name, objective in self._context.items():
            context[name] = reach(objective, data)

        nodes = reach(self._at, data)
        if isinstance(nodes, dict):
            nodes = nodes.values()

        if nodes is None:
            raise DGNoContent("Found no nodes at {}".format(self._at))

        for node in nodes:
            result = copy(context)
            for name, objective in self._objective.items():
                result[name] = reach(objective, node)
            yield result

    @staticmethod
    def _eval_extraction(name, objective, soup, el=None):
        try:
            return eval(objective) if objective else None
        except Exception as exc:
            raise ValueError("Can't extract '{}'".format(name)) from exc

    def text_xml(self, soup):  # soup used in eval!

        context = {}
        for name, objective in self._context.items():
            context[name] = self._eval_extraction(name, objective, soup)

        at = elements = self._eval_extraction("@", self._at, soup)
        if not isinstance(at, list):
            elements = [at]

        for el in elements:  # el used in eval!
            result = copy(context)
            for name, objective in self._objective.items():
                if not objective:
                    continue
                result[name] = self._eval_extraction(name, objective, soup, el)
            yield result
