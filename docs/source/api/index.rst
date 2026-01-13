API Reference
=============

Top-level package
-----------------

The main interface for ``cliasi``.

cliasi exports the :class:`~cliasi.Cliasi` instance :data:`~cliasi.cli`
as well as

* :data:`~cliasi.STDOUT_STREAM` standard output stream the library uses
* :data:`~cliasi.STDERR_STREAM` error stream the library uses
* :data:`~cliasi.SYMBOLS` collection of useful symbols
* :class:`~cliasi.constants.TextColor` color storage for terminal text
* :func:`~cliasi.logging_handler.install_logger` (to install it your own way, is done automatically)

.. py:data:: cliasi.cli
    :annotation: global cli instance
    :type: ~cliasi.cliasi.Cliasi

.. py:data:: cliasi.STDOUT_STREAM
    :annotation: io.TextIOWrapper

    standard output stream the library uses

.. py:data:: cliasi.STDERR_STREAM
    :type: io.TextIOWrapper

    Error stream the library uses

.. py:data:: cliasi.SYMBOLS

    Collection of useful symbols


Cliasi instance
-----------------
The main cliasi instance exposes various parameters to control behavior:

* :attr:`~cliasi.cliasi.Cliasi.messages_stay_in_one_line` - wether messages should stay in one line
* :attr:`~cliasi.cliasi.Cliasi.min_verbose_level` - verbosity level
* :attr:`~cliasi.cliasi.Cliasi.enable_colors` - whether to use colored output

.. automodule:: cliasi.cliasi
   :members:
   :undoc-members:
   :show-inheritance:


Constants (Animations)
------------------------

.. automodule:: cliasi.constants
   :members:
   :undoc-members:
   :show-inheritance:


logging handler
--------------------

.. automodule:: cliasi.logging_handler
   :members:
   :undoc-members:
   :show-inheritance:
