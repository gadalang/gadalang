from __future__ import annotations

__all__ = ["sanitize_node_name", "run", "main"]
import sys
import asyncio
import argparse
import json
from typing import Optional
from gadalang import nodes
import pygada_runtime


def sanitize_node_name(node: str) -> str:
    """Sanitize a node name:

    .. code-block:: python

        >>> import gadalang
        >>>
        >>> # Builtin node
        >>> gadalang.sanitize_node_name("json")
        'gadalang_lang.json'
        >>>
        >>> # Custom node
        >>> gadalang.sanitize_node_name("somepackage.somenode")
        'somepackage.somenode'
        >>>
        >>> # Invalid node
        >>> gadalang.sanitize_node_name("invalid")
        'invalid'
        >>>

    :param node: node name
    :return: node name
    """
    # Keep nodes containing one "." intact
    if "." in node:
        return node

    # Search for builtin node
    known = nodes.load()
    owner = known.get(node, None)
    if owner is None:
        return node

    return f"gadalang_{owner}.{node}"


def run(node: str, data: Optional[dict] = None) -> dict:
    """Run a gadalang node with input data and return node output:

    .. code-block:: python

        >>> import gadalang
        >>>
        >>> gadalang.run('json', data={"data": {"a": 1, "b": 2}})
        {'data': {'a': 1, 'b': 2}}
        >>>

    :param node: node to run
    :param data: node inputs
    :return: node output
    """
    # Run component
    data = data if data is not None else {}

    async def _run():
        with pygada_runtime.PipeStream() as stdin:
            with pygada_runtime.PipeStream() as stdout:
                with pygada_runtime.PipeStream(rmode="r") as stderr:
                    pygada_runtime.write_json(stdin, data)
                    stdin.eof()

                    proc = await pygada_runtime.run(
                        sanitize_node_name(node),
                        stdin=stdin.reader,
                        stdout=stdout,
                        stderr=stderr,
                    )

                    await proc.wait()

                    stdout.eof()
                    stderr.eof()

                    if proc.returncode != 0:
                        raise Exception(await stderr.read())

                    return await pygada_runtime.read_json(stdout)

    return asyncio.run(_run())


def main(argv: Optional[list[str]] = None, stdin: any = None):
    """Main entrypoint:

    .. code-block:: python

        >>> import gadalang
        >>>
        >>> gadalang.main(['gadalang', 'json', '-d', '{"data": {"a": 1, "b": 2}}'])
        {'data': {'a': 1, 'b': 2}}
        >>>

    Input data can be read from ``stdin``:

    .. code-block:: python

        >>> import gadalang
        >>> import pygada_runtime
        >>>
        >>> with pygada_runtime.PipeStream(wmode="w") as stdin:
        ...     # Write JSON object to stdin
        ...     stdin.write('{"data": {"a": 1, "b": 2}}')
        ...     stdin.eof()
        ...
        ...     # Pass stdin to gadalang
        ...     gadalang.main(['gadalang', 'json'], stdin=stdin.reader)
        {'data': {'a': 1, 'b': 2}}
        >>>

    :param argv: command line arguments
    :param stdin: input stream
    """
    argv = sys.argv if argv is None else argv
    stdin = sys.stdin if stdin is None else stdin

    parser = argparse.ArgumentParser(prog="Service", description="Help")
    parser.add_argument("node", type=str, help="command name")
    parser.add_argument("-d", "--data", help="input data")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbosity level")
    args = parser.parse_args(args=argv[1:])

    # Read input data from stdin or CLI
    if args.data is None or args.data == "-":
        data = json.loads(stdin.read())
    else:
        data = json.loads(args.data)

    # Run node
    output = run(node=args.node, data=data)

    # Write output data to stdout
    if output is not None:
        print(output)


if __name__ == "__main__":
    main(sys.argv)
