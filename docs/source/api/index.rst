API Reference
=============

Top-level package
-----------------

The main interface for ``cliasi``.

cliasi exports the :class:`~cliasi.Cliasi` instance :data:`~cliasi.cli`
as well as

* :data:`~cliasi.STDOUT_STREAM`
* :data:`~cliasi.STDERR_STREAM`
* :data:`~cliasi.SYMBOLS`
* :class:`~cliasi.constants.TextColor`
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

.. automodule:: cliasi
   :members: Cliasi, TextColor
   :show-inheritance:
   :imported-members:



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
