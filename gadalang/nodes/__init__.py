from __future__ import annotations

__all__ = ["load"]


def load_plugins() -> list:
    """Load all plugins registered in **gadalang.nodes**:

    .. code-block:: python

        >>> from gadalang import nodes
        >>>
        >>> nodes.load_plugins()
        [('lang', <module 'gadalang_lang._plugin' ...)]
        >>>

    :return: plugins
    """
    import sys
    import pkgutil
    import importlib
    import pkg_resources
    import functools

    def iter_namespace(ns_pkg):
        for finder, _, ispkg in pkgutil.iter_modules(
            ns_pkg.__path__, ns_pkg.__name__ + "."
        ):
            yield _, functools.partial(importlib.import_module, _)
        for _ in pkg_resources.iter_entry_points("gadalang.nodes"):
            yield "gadaland.nodes.{}".format(_.name), _.load

    def normalize(name):
        return name[name.rfind(".") + 1 :]

    # sys.modules[__name__] == this module
    return [(normalize(_), load()) for _, load in iter_namespace(sys.modules[__name__])]


def load() -> dict:
    """Load all nodes registered in **gadalang.nodes**:

    .. code-block:: python

        >>> from gadalang import nodes
        >>>
        >>> nodes.load()
        {'json': 'lang', 'yaml': 'lang'}
        >>>

    :return: nodes
    """
    nodes = {}
    for name, plugin in load_plugins():
        for _ in plugin.nodes():
            nodes[_] = name

    return nodes
