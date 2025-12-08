Welcome to the cliasi documentation!
======================================

Current version: |release|

Cliasi is a simple CLI library designed to enhance command-line interfaces with ease. It provides features like verbosity control, colorful outputs, and logging integration.

Get started in a minute using the guide below, or dive into the API reference.

Set up:
--------------
Install cliasi

.. code-block:: python
  :substitutions:

   pip install cliasi==|version|

Here is a quick example to get you started:

.. code-block:: python

    from cliasi import Cliasi

    cli = Cliasi(min_verbose_level=20, messages_stay_in_one_line=True, enable_colors=True)
    cli.info("Welcome to cliasi!")

.. toctree::
   :maxdepth: 2
   :caption: Guide

   getting_started
   advanced
   set_up_development_environment

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`