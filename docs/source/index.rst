.. singlejson documentation master file, created by
   sphinx-quickstart on Mon May 20 19:39:32 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the cliasi documentation!
======================================

Cliasi is a simple CLI library designed to enhance command-line interfaces with ease. It provides features like verbosity control, colorful outputs, and logging integration.

Get started in a minute using the guide below, or dive into the API reference.

Quick Example:
--------------

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

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`