.. _instances:

Cliasi instances
==================

Having multiple cliasi instances allows you to easily
communicate different program scopes.

Part A of your program has one instance with its own prefix
while part B has another instance with a different prefix.

:attr:`~cliasi.cliasi.Cliasi.min_verbose_level` **and**
:attr:`~cliasi.cliasi.Cliasi.messages_stay_in_one_line`
are inferred from the global (:data:`cliasi.cli`) instance if not set (None).

This means that if you set these parameters on the global instance,
all other instances will inherit these settings unless you explicitly set them.

.. code-block:: python
    :caption: examples/cliasi_multiple_instances.py

    from cliasi import Cliasi, cli

    def function_that_has_no_idea_about_main_program():
        # Create a new instance with its own prefix
        local_cli = Cliasi(prefix="FUNC")
        local_cli.log("Debug will be shown as min verbosity is inferred by default")
        local_cli.info("Info from function")

    cli.min_verbose_level=0
    cli.set_prefix("MAIN")
    cli.log("Shown as min verbosity is DEBUG")
    function_that_has_no_idea_about_main_program()

.. warning::
    The actual colors and symbols below may vary depending on your terminal and its settings.

.. raw:: html

    <div class="highlight-text notranslate">
    <div class="highlight"><pre>
    <span style="color: #888888">LOG [MAIN]  Shown as min verbosity is DEBUG</span>
    <span style="color: #888888">LOG [FUNC]  Debug will be shown as min verbosity is inferred by default</span>
    <span style="color: #ffffff; font-weight: bold">i</span> <span style="color: #888888">[FUNC]</span>  Info from function
    </pre></div>
    </div>
