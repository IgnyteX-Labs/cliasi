Setting up development environment
==================================

This document describes how to set up a development environment for building
and testing the documentation and running the test-suite locally.

This project is managed by uv.

A ``Makefile`` is provided for convenience to automate common development tasks.

Create a virtual environment and install the dev dependencies:

.. code-block:: bash

    # Using Makefile
    make install

    # Or directly with uv
    uv sync --group dev

This will both download dependencies to test and build the documentation.
Other possible dependency groups are ``test`` and ``docs``.

Pre commit checks with pre-commit
----------------------------------
This project uses `pre-commit <https://pre-commit.com/>`_ to manage git hooks for
code quality checks.
To install the git hooks, run:
.. code-block:: bash

    uv run --group dev pre-commit install

Running Tests and Linting
-------------------------

You can run all quality checks (lint, typecheck, and tests) using:

.. code-block:: bash

    make all

Individual checks:

.. code-block:: bash

    make lint       # Run ruff
    make typecheck  # Run mypy
    make test       # Run pytest

Building Documentation
----------------------

To build the HTML docs into "docs/build/html":

.. code-block:: bash

    # Using Makefile
    make docs

    # Or directly with uv
    uv run --group docs make html -C docs

The documentation uses asciinema to capture output from the terminal
from animations.
This cast is then converted to a gif using `aggcast`.
To update the animations, install `asciinema` and `aggcast` and then run
the following command from the root of the repository:

.. code-block:: bash

    make casts
    make casts-interactive
    make aggconvert
    make docs

This will re-generate all asciinema gifs in the documentation and update the documentation.



