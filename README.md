Abstract
========

This document is about implementing a new node-based programming language called gadalang (gada stands for bridge) over Python for coding simple tasks, complex tools, automated pipelines, or even standalone applications.

Motivation
==========

Problem
-------

Until now we write backend tools and automated pipelines using either `bat` or Python scripts.

And while Python is way more secure and easy to write than `bat`, writing a tool in a programming language always involve mastering complex libraries and dealing with a bunch of exceptions.

Think about how you would have to understand how `aiomysql` works, what is a pool, what are the `ContextManager` that you must close correctly, how to run the `async` code and wait for completion, deal with exceptions that can occur, just to code a simple tool connecting to a MySQL database.

Wouldn't it be easier to have some kind of pre-defined toolbox for the common use case of opening a connection to a MySQL database and closing it properly ?

Think about how you have to install Pillow and understand how to open an image, resize it, save it to file, and clean everything, just because didn't want to have to manually resize all your images with GIMP ?

Wouldn't it be easier to have a single node taking a list of files as input, resizing them, and saving the results to the disk ?

And what if I told you that those nodes could run Python code in the background ? And that you could easily write those nodes yourself, publish them in Python packages, and let others download them as easily as they would download a Python package via `pip` ?

This is what gadalang is about.

Not trying to create yet another programming language from scratch, not reinventing the wheel, not providing yet another package manager, not splitting the existing Python community, not forcing you to choose between Python or gadalang, but building something over and based on Python for taking advantage of what already exists.

State of the Art
----------------

Can't picture it yet ? Just think of how powerful and popular Github Actions have become:

```yml
jobs:
 tests:
  runs-on: ubuntu-latest
 
  steps:
  - uses: actions/checkout@v1
  - name: Set up Python 3.5.7
    uses: actions/setup-python@v1
    with:
     python-version: 3.5.7
  - name: Install dependencies
    run: pip install -r requirements.txt
  - name: Run tests
    run: python manage.py test
```

This is an example of an automated pipeline described in YAML and run when you push changes to the Github repository.

This example contains one step `actions/checkout@v1` which checkout the repository, then `actions/setup-python@v1` which install Python, then some steps for installing requirements and running tests.

As you can see, this is easy to describe a simple pipeline with a single YAML file.

But think about how it would have been complicated to write if you had to code it in Python ?

Github Actions are a great example of big individual tasks with concrete goals, that can be linked together for creating automated workflows.

However, Github Actions also have a drawback in that they are too close to the underlying OS: see how we run the command `pip install -r requirements.txt`. Another example is that you have to use environment variables for passing data between steps.

Like Github Actions, gadalang aims to:
  * Provide big nodes (or steps) for solving concrete goals (think of a toolbox).
  * Allow everyone to write their nodes and share them.
  * Allow to link those nodes together for creating complex and automated pipelines.

In comparison of Github Actions, gadalang aims to:
  * Run on your desktop, not only on Github.
  * Be platform-independent such as Python is.
  * Look more like a programming language where you can control the execution flow (think conditions, loops) and pass variables.

But why not use an already existing visual programming language ?

Well, there are many other visual programming languages, however they are often too low level or target a specific field of application, while gadalang will be a generic toolbox with as many use cases as Python, and not as low level as a real programming language.

It will be at a lower level than Github Actions, allowing to control the execution flow and use variables as in any programming language, but it will never replace the genericity or the powerness of low level code writen in a programming language like Python or C/C++.

So What is Gadalang ?
---------------------

The main goal of gadalang is to be a meta language over Python, and make it simpler to write complex tasks by linking big nodes together. Those nodes will be running Python code under the hood, so they can use existing Python libraries. But the goal is not to allow coding basic functions such as Fibonacci directly using nodes.

If you were to make a Fibonacci node or a AStar node, the best way would be to code it in Python and wrap it in a node so it can be used in gadalang.

Interface With Other Languages
------------------------------

Additionnaly, the ultimate goal of gadalang is to bridge Python with any other existing language.

This is something already done when you install a Python package that wraps a library or executable written in another language.

Gadalang aims to have a protocol, common to any language, for passing data between nodes, and allowing to implement nodes in any language.

Gadalang also aims to provide runtimes implemented in all supported languages, to ease the process of running nodes and sending/receiving data from another language.

TLDR
----

Gadalang is:
  * A meta language/extension over Python.
  * YAML description of nodes connected to each others.
  * Collection of nodes solving concrete goals and implemented in Python or any other language.
  * Taking advantage of `pip` for distributing nodes around the world.
  * Visual programming language (far in the future to be honest).

Gadalang is not:
  * Another programming language to learn.
  * Low level enough for coding basic functions such as Fibonacci or quicksort.

Specification
=============

The previous part was a lot of theories, but now come the implementation ideas. And you will see that besides coding a complete and stable visual editor which will take years, there is nothing complicated about gadalang.

Implemented Over Python
-----------------------

Gadalang is by itself a Python package published to `PyPi` that can be installed with:

```bash
$ python -m pip install gada
```

Along with the package, it installs the following command line:

```bash
$ gada
usage: gada [-h] [-v] node ...

Help

positional arguments:
  node           command name
  argv           additional CLI arguments

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Verbosity level
```

As you would run a Python program with `python foo.py`, you can run a gada program with:
```bash
$ gada foo.yml
```

Note the `.yml` extension. This is important because gada programs and nodes are written in YAML which is easy to write and read.

Hello World
-----------

This is how you would write a gada program that outputs `hello world`:

```yml
# hello_world.yml
steps:
- name: print
  inputs:
    in: hello world
```

Run with:
```
$ gada hello_world.yml
hello world
```

Structure of a Program
----------------------

A gada program is different from a gada node in the same way a Python program is different from a Python library.

This is the structure of a gada program described in YAML:
```yml
# resize_image.yml
name: resize_image
inputs:
- name: input
  type: list
  help: input images to resize
- name: output
  type: str
  help: output directory
  optional: true
  default: .
- name: width
  type: number
  help: new width
  optional: true
- name: height
  type: number
  help: new height
  optional: true
steps:
- name: imaging/resize
  inputs:
    input: "{{ input }}"
    width: "{{ width }}"
    height: "{{ height }}"
```

The first part contains metadata:
```yml
name: resize_image
inputs:
- name: input
  type: list
  help: input images to resize
- name: output
  type: str
  help: output directory
  optional: true
  default: .
- name: width
  type: number
  help: new width
  optional: true
- name: height
  type: number
  help: new height
  optional: true
```

This is where we define the inputs and outputs of our program. The syntax has been chosen so that those metadata can be easily mapped to `argparse` for command-line validation and generation of help messages.

Running this program with `-h` displays the following message:
```bash
$ gada resize_image.yml -h
usage: resize_image [-h] [-v] [--output] [--width] [--height] input

Help

positional arguments:
  input          input images to resize

optional arguments:
  --output       output directory
  --width        new width
  --height       new height
  -h, --help     show this help message and exit
  -v, --verbose  Verbosity level
```

The second part describes the nodes our gada program will run:
```yml
steps:
- name: imaging/resize
  inputs:
    input: "{{ input }}"
    width: "{{ width }}"
    height: "{{ height }}"
```

Resizing an image is such a common use case, of course there is a builtin gada node for that.

This node is called `resize` and resides in the `imaging` package. So specifying `imaging/resize` makes gada searches the node `resize` in the `imaging` package.

The arguments `input`, `width`, and `height` are passed exactly as you would do in Python with keyword arguments. So don't be surprised to see the same names on the left side and the right side.

Run this program exactly like you would run a Python program:
```bash
$ gada resize_image.yml --width 0.5 --height 0.5 foo.png
```

What is a Node ?
----------------

Let's start with a simple example of a Python package providing an `hello_world` node:

```
helloworld/
├─ helloworld/
│  ├─ __init__.py
│  ├─ config.yml
├─ setup.py
```

The nodes must be defined in `config.yml` at the root of the Python package:
```yaml
# config.yml
nodes:
- name: hello_world
  runner: pymodule
  entrypoint: hello_world
```

The node is implemented in `__init__.py`:
```python
# __init__.py
from pygada_runtime import node

@node
def hello_world(*args, **kwargs):
  print("hello world")
```

What `config.yml` does, is basically telling gada that our node must be run with `pymodule` runner (an additional Python package providing a runner capable of calling functions declared in Python modules), and that the function to run is `hello_world`.

First, the package must be installed with:
```bash
$ python setup.py install
```

Then you can write the following program:
```yaml
# hello_world.yml
steps:
- name: helloworld/hello_world
```

And run it with:
```bash
$ gada hello_world.yml
hello world
```

When you install the package with `python setup.py install` , you end up with:
```
lib/
├─ site-packages/
   ├─ helloworld/
   │  ├─ __init__.py
   │  ├─ config.yml
```

So, when gada searches for `helloworld/hello_world` node, it first tries to find an installed `helloworld` package, then gets it's absolute path, then parses the `config.yml` file located at the root.

This structure allows gada to quickly find installed nodes without having to scan all installed Python packages.

Nodes with Inputs and Outputs
-----------------------------

Now, here is an example of a node expecting input parameters and generating output parameters:

```yaml
# config.yml
nodes:
- name: sum
  runner: pymodule
  entrypoint: sum
  inputs:
  - name: a
    type: number
  - name: b
    type: number
  outputs:
  - name: out
    type: number
```

Implementation:
```python
# __init__.py
from pygada_runtime import node

@node
def sum(a: int | float, b: int | float) -> dict:
  return {"out": a + b}
```

Node Overload
-------------

We can have multiple nodes with the same name but different signatures:

```yaml
# config.yml
nodes:
- name: max
  runner: pymodule
  entrypoint: max_number
  inputs:
  - name: a
    type: number
  - name: b
    type: number
  outputs:
  - name: out
    type: number
- name: max
  runner: pymodule
  entrypoint: max_str
  inputs:
  - name: a
    type: str
  - name: b
    type: str
  outputs:
  - name: out
    type: str
```

Implementation:
```python
# __init__.py
from pygada_runtime import node

@node
def max_int(a: int | float, b: int | float) -> dict:
  return {"out": max(a, b)}

@node
def max_str(a: str, b: str) -> dict:
  return {"out": max(a, b)}
```

The node with the best matching signature will be chosen:
```yaml
# max.yml
steps:
- name: mypackage/max
  inputs:
    a: "abc"
    b: "abcdef"

# max.yml
steps:
- name: mypackage/max
  inputs:
    a: 1
    b: 2
```

Multiple Outputs
----------------

As gada is a dynamic language, it's easy to allow for multiple outputs:

```yaml
# config.yml
nodes:
- name: foo
  runner: pymodule
  entrypoint: foo
  outputs:
  - name: a
    type: number
  - name: b
    type: number
```

Implementation:
```python
# __init__.py
from pygada_runtime import node

@node
def foo() -> dict:
  return {"a": ..., "b": ...}
```

Passing Variables
-----------------

Here comes the special `"{{ var }}"` syntax to assign or read variables.

With the YAML syntax, loading the following config would give a dict containing `{"a": "hello", "b": "world"}`, and this is totally fine if we want to pass strings to a node.
```yaml
# max.yml
steps:
- name: mypackage/max
  inputs:
    a: hello
    b: world
```

But what if we want to refer to a existing `hello` variable instead of a string ?

The syntax for making reference to variables global to the program is:

```yaml
# max.yml
inputs:
- name: hello
  type: str
- name: world
  type: str
steps:
- name: mypackage/max
  inputs:
    a: "{{ hello }}"
    b: "{{ world }}"
```

When gada sees `"{{ hello }}"`, it replaces the value by the content of the `hello` variable if defined.

You can also reference outputs of nodes with an unique id:

```yaml
# max.yml
steps:
- name: mypackage/max
  id: foo
  inputs:
    a: hello
    b: world
- name: print
  inputs:
    in: "{{ foo.out }}"
```

Node Reference
--------------

Now you know how to store the result of a node in a variable and pass it to another node.

But as you may be familiar with if you are already experienced with node-based programming, you often have to link two nodes that are far away in the execution flow. Or maybe that you will simply use twice the same node in your program and you want to reference the output of one of them.

This is the reason why you can assign unique ids to the nodes of your program:

```yaml
# max.yml
steps:
- name: mypackage/max
  id: some_unique_id
  inputs:
    a: hello
    b: world
# ...
# many nodes in-between
# ...
- name: print
  inputs:
    in: "{{ some_unique_id.out }}"
```

Note that you don't have to explicitely store the output of a node into a variable. Gada will remember the output of each node in the current scope and let you reference the output with `"{{ id_of_the_node.output_name }}"`.

Note: this `id` parameter allows a visual editor to generate the program and correctly link nodes together and without conflict by assigning a GUID to each node.

Control Flow
------------

So far, the programs showed as examples were all linear and executed from start to end.

But gada has special builtin nodes for controlling the execution flow:

```yaml
# max.yml
inputs:
- name: a
  type: number
- name: b
  type: number
steps:
- name: gt
  inputs:
    a: "{{ a }}"
    b: "{{ b }}"
  outputs:
    then:
    - name: print
      inputs:
        in: a is greater than b
    else:
    - name: print
      inputs:
        in: b is greater than a
```

This may look like a lot of work only for comparing two numbers, but remember that gada is not about coding basic functions with nodes but rather assembling multiple nodes, each performing a complicated task, together.

At the implementation level, you may be curious to know what happens when gada encounters:
```yaml
  then:
  - name: print
```

Indeed, you learned that you could pass parameters with `input: value` or capture results with `output: "{{ var }}"`. So why are we passing a node in this situation ?

In fact there is a special `exec` type that can be used on output parameters of a node. This is how you would describe the `gt` node yourself:

```yaml
nodes:
- name: gt
  runner: pymodule
  entrypoint: greater_than
  inputs:
  - name: a
    type: number
  - name: b
    type: number
  outputs:
  - name: then
    type: exec
  - name: else
    type: exec
```

Implementation:
```python
# __init__.py
from pygada_runtime import node

@node
def greater_than(a: int | float, b: int | float) -> dict:
  return {"then": True} if a >= b else {"else": True}
```

When gada receive `True` for an output flagged as `exec`, it knows that it must execute the node assigned to that output.

Pure Nodes
----------

Nodes can either be exec nodes or pure nodes.

An exec node is a node with an input exec pin linked to the output exec pin of another exec node. In gada this is implicitly done by listing all the nodes in your program:

```yaml
# foo.yml
steps:
- name: first_node
- name: second_node
```

Here `second_node` is implicitly linked to `first_node` and will be executed after it.

A pure node is a node without an input exec pin and that is executed only when another node references its output. This also means that a pure node could be placed anywhere in your program and even referenced by multiple nodes.

It may seem complicated, but is in fact easily implemented in gada.

All nodes are marked as exec nodes by default, but you can mark a node as pure with:

```yaml
nodes:
- name: pi
  runner: pymodule
  entrypoint: pi
  pure: true
  outputs:
  - name: out
    type: number
```

A node marked as pure will never be executed when gada encounters it. Instead it will be stored in memory like any other nodes, and will be executed only when another node references one of its outputs:

```yaml
# foo.yml
steps:
- name: pi
  id: pi_node
- name: print
  inputs:
    in: "{{ pi_node.out }}"
```

This means that those nodes can be placed anywhere in your program as long they are placed before any node that references them:

```yaml
# foo.yml
steps:
- name: pi
  id: pi_node
# ...
# more nodes
# ...
- name: if
  inputs:
    in: "{{ condition }}"
  outputs:
    then:
    - name: print
      inputs:
        in: "{{ pi_node.out }}"
    else:
    - name: print
      inputs:
        in: "{{ pi_node.out }}"
```

Note: this design simplifies how a visual editor can generate the program by allowing it to output the pure nodes almost anywhere in the execution flow.

Overview of Gada Packages
=========================

Gada is composed of many packages.

Scope of `gada` Package
-----------------------

The gada package by itself is a lightweight package that only knows how to locate nodes installed in `site-packages` and parse their configuration.

gada expects plugins providing what we call `runners`, to be installed alongside for effectively running nodes.

gada has a default generic runner for running any command line even if it's encouraged to install a runner specific to the language your node is written in:

```yaml
nodes:
- name: foo
  runner: generic
  command: scalac ${file}
  file: Foo.scala
```

If you understood well how gada is working and running nodes, you know that each node will in fact be run in a new process (the runner) independent of gada.

So you may ask yourself where the program memory will be stored and how variables will be passed between nodes.

Well, all the memory will be kept inside of the instance of gada spawned with the command:
```bash
$ gada foo.yml
```

And variables will be passed from gada to runners and from runners to gada by serializing and deserializing data on-the-fly.

You may think that this is a considerable loss of performances when running a program. But remember that the goal of gada is not to replace a low level programming language, but to ease the creation of automated pipelines for backend tools or build systems.

So of course gada will never be fast enough for coding the next AAA game.

Scope of `gada-pyrunner` Package
--------------------------------

This package is the Python implementation of a gada runner for running nodes written in Python.

The configuration is:
```yaml
nodes:
- name: foo
  runner: pymodule
  entrypoint: foo
```

Under the hood this will import the module containing the node, and call the `foo` function if it exists.

Note: the goal is to have one `gada-xrunner` package for each supported language.

Scope of `pygada-runtime` package
---------------------------------

This package is a runtime library for writing nodes in Python. It takes care of hidding all the boilerplate required for decoding/encoding parameters passed between nodes:

```python
from pygada_runtime import node

@node
def foo(*args, **kwargs):
  return {...}
```

Scope of `cgada-runtime` package
--------------------------------

This package is the equivalent of `pygada-runtime` for C/C++.

Scope of `gadalang-lang` package
--------------------------------

This is a package containing a collection of official nodes for gada.

It will contain nodes such as `print`, `open`, `if`, `for`, `max`, `min`, ...

Scope of `gadalang-imaging` package
-----------------------------------

This package will contain a collection of imaging related nodes.

Milestones
==========

V1 - The "I just want a proof of concept":
  * gada can:
    * be installed as a Python package
    * run on the command line
    * parse a program description
    * locate nodes installed in `site-packages`
    * parse a node description
    * run nodes in a sequence
  * gada-pyrunner can:
    * be installed as a Python package
    * install as a gada runner (plugin)
    * be called by gada
    * run a Python node
  
V2 - The "Okay now let's pass some hard-coded data to nodes":
  * gada can:
    * serialize/deserialize primitive data
  * gada-pyrunner can:
    * serialize/deserialize primitive data
  * pygada-runtime can:
    * be installed as a Python package
    * wrap a Python function for making it a gada-pyrunner compatible node
    * map data received from gada-pyrunner to the function parameters
    * map the function return to data sent by gada-pyrunner
  
V3 - The "Hard-coded data are cool but I'd like to use variables":
  * gada can:
    * parse variables declared with the `"{{ var }}"` syntax
    * replace variables in the program by their value
    * link variables to inputs and outputs
    * handle program inputs from the command line
  
V4 - The "Let's control the flow":
  * gada can:
    * handle nodes with `exec` outputs
    * handle pure nodes
    * handle node overload
  
V5 - The "I offer you a standard library":
  * write the gadalang-lang package
  * official collection of core nodes such as `print`, `if`, `for`, `max`, `min`,...
  * gada:
    * understand that nodes without a namespace are from the official collection
    * search for those nodes directly in the gadalang-lang package
  
V6 - The "Let's explore new horizons":
  * gada-crunner can:
    * be installed as a Python package
    * install as a gada runner (plugin)
    * be called by gada
    * run a C/C++ node (probably dll)
    * serialize/deserialize primitive data
  * cgada-runtime can:
    * be included as a library in a C/C++ project
    * wrap a C/C++ function for making it a gada-crunner compatible node
    * serialize/deserialize primitive data
    * map data received from gada-crunner to the function parameters
    * map the function return to data sent by gada-crunner
  
...
  
V100 - The "I don't want to nano anymore":
  * build a visual editor

Reference Implementation
========================

The implementation started at https://github.com/gadalang.

All contributions are welcome.
