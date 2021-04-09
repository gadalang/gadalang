import gadalang


def test_run():
    """Test running a custom node.
    """
    output = gadalang.run("testnodes.hello")
    assert output == {"data": "hello"}, "wrong output"
