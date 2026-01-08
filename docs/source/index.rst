cliasi
========

is a tiny command-line interface (CLI) library for Python.

It is meant to be simple and easy to use, while providing useful features for building
hobby project command-line applications. It offers

* Pre-configured global instance for quick usage.
* support for logging
* colored output
* progress bars and animations
* message types similar to logging

Set up:
--------------
Install with pip / uv:

.. code-block:: python
  :substitutions:

  pip install cliasi==|release|
  uv add cliasi==|release|


Here is a quick example to get you started:

.. code-block:: python

    from cliasi import Cliasi

    cli = Cliasi(min_verbose_level=20, messages_stay_in_one_line=True, enable_colors=True)
    cli.success("Installation successful!")
    cli.set_prefix("hobby_app")
    progressbar = cli.progressbar_animated_download("Downloading...")
    # Do some downloading work here...
    progressbar.update(70)
    # Finish download
    progressbar.stop()
    cli.success("Download complete!")

All of this text will stay in one line.

Why cliasi
------------

Cliasi is small and primarily designed for basic animations
and progressbars.

* Minimal API with sensible defaults (see about options here :ref:`instances`).
* Supports logging levels for verbosity control.
* Will auto-format exceptions from other libraries :ref:`logging_integration`
* Wide variety of message types all named unambiguously. :ref:`message_types`
* Disappearing messages to keep the terminal clean. (:attr:`~cliasi.Cliasi.messages_stay_in_one_line` option)
* Prefix system to indicate program scope. :ref:`instances`

Note on windows support
-------------------------

I do not own a windows device so windows support is untested.
If there are any issues please open an issue on GitHub or
feel free to open a PR with fixes.


Further reading
"""""""""""""""""

.. toctree::
  :maxdepth: 1
  :caption: Guide
  :glob:

  cliasi_instance
  message_types
  logging_handler
  development

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`