.. _logging_integration:

Logging Integration
====================

`cliasi` can automatically handle logs from Python's standard `logging` module.
By default, the global :data:`~cliasi.cli` instance is already set up to handle logs.

.. code-block:: python

    from cliasi import cli
    import logging

    # Get a logger
    logger = logging.getLogger("my_app")
    logger.setLevel(logging.INFO)

    # Log messages like these will also be displayed by cliasi (using the global cli instance)
    logger.info("This is a log message.")
    # > i [CLI] | This is a log message.
    logger.warning("This is a warning from the logger.")
    # > ! [CLI] | This is a warning from the logger.
    cli.set_prefix("LOGGER")
    # Changing the global prefix will result in updated prefixes for log messages too
    logger.error("This is an error from the logger.")
    # > X [LOGGER] | This is an error from the logger.

Exception and Traceback Formatting
------------------------------------

By default, `cliasi` will also format exceptions and tracebacks from logged errors.
It will use the `fail` message style to display them.

Example:

Installing the logging handler yourself
------------------------------------------

If you have problems with logs getting displayed multiple times
maybe try running ``install_logger`` with ``replace_root_handlers=True``.
This will remove all existing root handlers before installing the cliasi default one.

.. code-block:: python
    :caption: Call this code once at the start of your program

    from cliasi import cli, install_logger

    # Will overwrite all existing root log handlers
    install_logger(cli, replace_root_handlers=True)
