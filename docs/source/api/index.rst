API Reference
=============

Top-level package
-----------------

The main interface for :mod:`~cliasi.cliasi`.

cliasi exports the :class:`~cliasi.cliasi.Cliasi` instance :data:`~cliasi.cli`
as well as

* :data:`~cliasi.STDOUT_STREAM` standard output stream the library uses
* :data:`~cliasi.STDERR_STREAM` error stream the library uses
* :data:`~cliasi.SYMBOLS` collection of useful symbols
* :class:`~cliasi.constants.TextColor` color storage for terminal text
* :class:`~cliasi.constants.CursorPos` to set position of cursor on interactive methods
* :class:`~cliasi.constants.PBCalculationMode` progress bar calculation modes.
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

* :attr:`~cliasi.cliasi.Cliasi.messages_stay_in_one_line` - whether messages should stay in one line, see :ref:`instances`
* :attr:`~cliasi.cliasi.Cliasi.min_verbose_level` - verbosity level, see :ref:`instances`
* :attr:`~cliasi.cliasi.Cliasi.enable_colors` - weather to use colored output
* :attr:`~cliasi.cliasi.Cliasi.max_dead_space` - maximum number of empty space between aligned messages :ref:`max_dead_space`

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
