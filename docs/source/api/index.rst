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

.. autodata:: cliasi.cli
.. autodata:: cliasi.STDOUT_STREAM
.. autodata:: cliasi.STDERR_STREAM
.. autodata:: cliasi.SYMBOLS

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
   :no-index:


``logging`` handler
--------------------

.. automodule:: cliasi.logging_handler
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
