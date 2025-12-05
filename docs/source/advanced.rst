Advanced usage
==============

Logging Integration
-------------------

`cliasi` can automatically handle logs from Python's standard `logging` module.
By default, the global `cli` instance is already set up to handle logs.

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

If you have problems with logs getting displayed multiple times maybe try running ``install_logger`` with ``replace_root_handlers=True``.
This will remove all existing root handlers before installing the cliasi default one.

.. code-block:: python

    from cliasi import cli, install_logger

    # Install the logger for this instance
    install_logger(cli, replace_root_handlers=True)

Animations and Progress Bars
----------------------------

`cliasi` provides tools for displaying progress and animations.

**Blocking Animation**
Blocking animations run in the main thread and block further execution until complete.

.. code-block:: python

    from cliasi import cli
    import time

    cli.animate_message_blocking("Saving.. [CRTL-C] to stop", time=3)
    # You cant do anything else while the animation is running
    # Useful if you save something to a file at the end of a program
    # User can CRTL-C while this is running
    cli.success("Data saved!")

**Non-Blocking Animation**

.. code-block:: python

    from cliasi import cli
    import time

    task = cli.animate_message_non_blocking("Processing...")
    # Do other stuff while the animation is running
    time.sleep(5)  # Simulate a long task
    cli.messages_stay_in_one_line = True  # To hide animation after finished.
    task.stop()  # Stop the animation when done
    cli.success("Done!")

**Progress Bars**

.. code-block:: python

    from cliasi import cli
    import time

    for i in range(101):
        cli.progressbar("Calculating", progress=i, show_percent=True)
        time.sleep(0.02)
    cli.newline() # Add a newline after the progress bar is complete
    cli.success("Calculation complete.")
    # Use cli.progressbar_download() for download-style progress bars.

**Animated Progress Bars**

.. code-block:: python

    from cliasi import cli
    import time

    task = cli.progressbar_animated_download("Downloading", total=100)
    for i in range(100):
        time.sleep(0.05)  # Simulate work
        task.update(1)    # Update progress by 1
    task.stop()        # Finish the progress bar
    cli.success("Download complete.")

User Input
----------

You can ask for user input, including passwords.

.. code-block:: python

    from cliasi import cli

    name = cli.ask("What is your name?")
    password = cli.ask("Enter your password:", hide_input=True)

    cli.info(f"Hello, {name}!")

