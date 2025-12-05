Getting started
===============

Installation
------------

.. code-block:: bash

   pip install cliasi

Quickstart
----------

.. code-block:: python

    from cliasi import cli  # Global Cliasi instance
    import logging

    cli.info("This is an informational message.")
    # > i [CLI] | This is an informational message.
    cli.success("Operation completed successfully!")
    # > ✔ [CLI] | Operation completed successfully!
    cli.messages_stay_in_one_line = True
    # Messages will stay in one line after this
    cli.warn("This is a warning message.")
    # > ! [CLI] | This is a warning message.
    cli.fail("An error occurred!")
    # > X [CLI] | An error occurred!
    # Debug messages are hidden by default as default verbostiy level is INFO
    cli.log("This is a debug message (only shown with high verbosity).")
    # > (no output)
    cli.min_verbose_level = logging.DEBUG

messages_stay_in_one_line
--------------------------

When ``messages_stay_in_one_line`` is set to ``True``, all subsequent messagesfinish
will overwrite the previous message instead of creating a new line. This is useful for progress updates or status messages.
<br> This is disabled by default so enable it using ``cli.messages_stay_in_one_line = True``. or pass ``Cliasi(prefix="CLI", messages_stay_in_one_line=True)`` when creating a new instance.

Cliasi instances
-----------------
You can also create your own instance to customize its behavior.
<br>This is especially helpful when giving over control to other parts of your application.
The new instance will copy the global verbosity setting when no verbosity is specified.

.. code-block:: python

    # Other part of your application that doesn't know what prefix to use
    from cliasi import Cliasi
    import logging

    # Create a new instance with a custom prefix and higher verbosity
    my_cli = Cliasi(prefix="APP")
    # Verbosity is blank so global setting is used

    my_cli.log_small("This is a debug message from my_cli.")  # Will be shown as global verbosity is DEBUG now
    # > l [APP] | This is a debug message from my_cli.

    # Cliasi will also do line breaks
    my_cli.info("This is an info message from my_cli.\n This is after a line break.")
    # > i [APP] | This is an info message from my_cli.
    # >         | This is after a line break.

You can view more about animations and progressbars in the advanced guide.

Features
--------

- Progress bars and animations.
- Simple and intuitive API.
- Pre-configured global instance for convenience.
- Verbosity control based on Python's `logging` levels.
- Colorful and formatted output for better readability.
- Seamless integration with Python's `logging` module.
- Global exception hook to catch and display uncaught exceptions.
