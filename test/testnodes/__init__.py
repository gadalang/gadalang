import sys
import pygada_runtime


def hello(argv, *args, **kwargs):
    pygada_runtime.write_json(sys.stdout, {"data": "hello"})
