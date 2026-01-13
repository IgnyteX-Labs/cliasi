.. _message_types:

Message types and animations
==============================

You can view example output of the library using the
python scripts in the provided examples directory.

Basic Message Types
--------------------

``cliasi`` provides several methods for common message types, each with its own symbol and color.

Here is how they look in the console:

.. code-block:: python
    :caption: examples/basic_messages.py

    from cliasi import cli

    cli.info("Starting process...")
    cli.success("Process completed!")
    cli.warn("Disk space is low.")
    cli.fail("Failed to connect to server.")
    cli.log("Debug info")
    cli.list("List item")

.. warning::
    The actual colors and symbols below may vary depending on your terminal and its settings.

.. raw:: html

    <div class="highlight-text notranslate">
    <div class="highlight"><pre>
    <span style="color: #ffffff; font-weight: bold">i</span> <span style="color: #888888">[CLI]</span> | Starting process...
    <span style="color: #00ff00; font-weight: bold">✔</span> <span style="color: #888888">[CLI]</span> | <span style="color: #00ff00">Process completed!</span>
    <span style="color: #ffff00; font-weight: bold">!</span> <span style="color: #888888">[CLI]</span> | <span style="color: #ffff00">Disk space is low.</span>
    <span style="color: #ff5959; font-weight: bold">X</span> <span style="color: #888888">[CLI]</span> | <span style="color: #ff5959">Failed to connect to server.</span>
    <span style="color: #888888">LOG [CLI] | Debug info</span>
    <span style="color: #ffffff; font-weight: bold">-</span> <span style="color: #888888">[CLI]</span> | List item
    </pre></div>
    </div>

Exception and Traceback Formatting
"""""""""""""""""""""""""""""""""""""
If an exception is raised or a traceback is logged, it will be formatted using the `fail` message style:

.. code-block:: python
    :caption: examples/exception_message.py

    import cliasi

    # Importing cliasi automatically installs the logging handler
    raise ValueError("An example error")

.. raw:: html
    .. note::

    <div class="highlight-text notranslate">
    <div class="highlight"><pre>
    <span style="color: #ff5959; font-weight: bold">X</span> <span style="color: #888888">[CLI]</span> | <span style="color: #ff5959">Uncaught exception:</span>
    <span style="color: #ff5959; font-weight: bold">X</span> <span style="color: #888888">[CLI]</span> | <span style="color: #ff5959">Traceback (most recent call last):
            </span>|<span style="color: #ff5959">   File "examples/exception_message.py", line 4, in &lt;module&gt;
            </span>|<span style="color: #ff5959">     raise ValueError("An example error")
            </span>|<span style="color: #ff5959"> ValueError: An example error</span>
    </pre></div>
    </div>

Animations and Progress Bars
----------------------------

Blocking Animation
"""""""""""""""""""""
Blocking animations run in the main thread and block further execution until complete.

.. code-block:: python
    :caption: examples/blocking_animation.py

    from cliasi import cli
    import time

    cli.animate_message_blocking("Saving.. [CTRL-C] to stop", time=3)
    # You cant do anything else while the animation is running
    # Useful if you save something to a file at the end of a program
    # User can CTRL-C while this is running
    cli.success("Data saved!")

.. raw:: html

   <div class="asciinema-demo">
        <img src="_static/asciinema/blocking_animation_demo-light.gif"
          class="asciinema_demo-light"
          alt="Blocking animation (light theme)">
        <img src="_static/asciinema/blocking_animation_demo-dark.gif"
          class="asciinema_demo-dark"
          alt="Blocking animation (dark theme)">
   </div>

Non-Blocking Animation
"""""""""""""""""""""""

.. code-block:: python
    :caption: examples/non_blocking_animation.py

    import time

    from cliasi import cli

    cli.messages_stay_in_one_line = True  # To hide animation after finished.
    task = cli.animate_message_non_blocking("Processing...")
    # Do other stuff while the animation is running
    time.sleep(3)  # Simulate a long task
    task.stop()  # Stop the animation when done
    cli.success("Done!")

.. raw:: html

    <div class="asciinema-demo">
        <img src="_static/asciinema/non_blocking_animation_demo-light.gif"
          class="asciinema_demo-light"
          alt="Non Blocking animation (light theme)">
        <img src="_static/asciinema/non_blocking_animation_demo-dark.gif"
          class="asciinema_demo-dark"
          alt="Non Blocking animation (dark theme)">
   </div>

Progress Bars
""""""""""""""""""

.. code-block:: python
    :caption: examples/progress_bar.py

    import time

    from cliasi import cli

    for i in range(101):
        cli.progressbar("Calculating", progress=i, show_percent=True)
        time.sleep(0.02)
    cli.newline()  # Add a newline after the progress bar is complete
    cli.success("Calculation complete.")
    # Use cli.progressbar_download() for download-style progress bars.

.. raw:: html

    <div class="asciinema-demo">
        <img src="_static/asciinema/progress_bar_demo-light.gif"
          class="asciinema_demo-light"
          alt="Progress Bar (light theme)">
        <img src="_static/asciinema/progress_bar_demo-dark.gif"
          class="asciinema_demo-dark"
          alt="Progress Bar (dark theme)">
   </div>

Animated Progress Bars
""""""""""""""""""""""""""
.. code-block:: python
    :caption: examples/animated_progress_bar.py

    import time

    from cliasi import cli

    task = cli.progressbar_animated_download("Downloading", )
    for i in range(100):
        time.sleep(0.05)  # Simulate work
        task.update(progress=i)    # Update progress by 1
    task.stop()        # Finish the progress bar
    cli.success("Download complete.")

.. raw:: html

    <div class="asciinema-demo">
        <img src="_static/asciinema/animated_progress_bar_demo-light.gif"
          class="asciinema_demo-light"
          alt="Animated Progress Bar (light theme)">
        <img src="_static/asciinema/animated_progress_bar_demo-dark.gif"
          class="asciinema_demo-dark"
          alt="Animated Progress Bar (dark theme)">
    </div>

User Input
""""""""""""

You can ask for user input, including passwords.

.. code-block:: python
    :caption: examples/user_input_interactive.py

    from cliasi import cli

    name = cli.ask("What is your name?")
    code = cli.ask("Enter your secret code:", hide_input=True)

    cli.info(f"Hello, {name} with code {code}")

.. raw:: html

    <div class="asciinema-demo">
        <img src="_static/asciinema/user_input_interactive-light.gif"
          class="asciinema_demo-light"
          alt="User input (light theme)">
        <img src="_static/asciinema/user_input_interactive-dark.gif"
          class="asciinema_demo-dark"
          alt="User input (dark theme)">
    </div>
