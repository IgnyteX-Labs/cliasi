.. _message_types:

Message types and animations
==============================

Basic Message Types
--------------------

``cliasi`` provides several methods for common message types, each with its own symbol and color.

Here is how they look in the console:

.. code-block:: python

    from cliasi import cli

    cli.info("Starting process...")
    cli.success("Process completed!")
    cli.warn("Disk space is low.")
    cli.fail("Failed to connect to server.")
    cli.log("Debug info")
    cli.list("List item")

.. raw:: html
    .. note::
    The output above is a simulation of how it appears in a terminal with color support.

    <div class="highlight-text notranslate">
    <div class="highlight"><pre>
    <span style="color: #ffffff; font-weight: bold">i</span> <span style="color: #888888">[CLI]</span> | Starting process...
    <span style="color: #00ff00; font-weight: bold">✔</span> <span style="color: #888888">[CLI]</span> | <span style="color: #00ff00">Process completed!</span>
    <span style="color: #ffff00; font-weight: bold">!</span> <span style="color: #888888">[CLI]</span> | <span style="color: #ffff00">Disk space is low.</span>
    <span style="color: #ff0000; font-weight: bold">X</span> <span style="color: #888888">[CLI]</span> | <span style="color: #ff0000">Failed to connect to server.</span>
    <span style="color: #888888">LOG [CLI] | Debug info</span>
    <span style="color: #ffffff; font-weight: bold">-</span> <span style="color: #888888">[CLI]</span> | List item
    </pre></div>
    </div>


Animations and Progress Bars
----------------------------

`cliasi` provides tools for displaying progress and animations.

**Blocking Animation**
Blocking animations run in the main thread and block further execution until complete.

.. code-block:: python

    from cliasi import cli
    import time

    cli.animate_message_blocking("Saving.. [CTRL-C] to stop", time=3)
    # You cant do anything else while the animation is running
    # Useful if you save something to a file at the end of a program
    # User can CTRL-C while this is running
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

