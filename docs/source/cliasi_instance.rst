.. _instances:

Cliasi instances
==================

Having multiple cliasi instances allows you to easily
communicate different program scopes.

Part A of your program has one instance with its own prefix
while part B has another instance with a different prefix.

.. code-block:: python

    from cliasi import Cliasi

    def scope_1():
        cli = Cliasi("scope_1")
        cli.success("Message will be prefixed with [scope_1]")

    def scope_2():
        cli = Cliasi("scope_2")
        cli.warning("Message will be prefixed with [scope_2]")

Global inference
"""""""""""""""""
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
    <span style="color: #888888">LOG [MAIN] </span><span>| Shown as min verbosity is DEBUG</span>
    <span style="color: #888888">LOG [FUNC] </span><span>| Debug will be shown as min verbosity is inferred by default</span>
    <span style="color: #ffffff; font-weight: bold">i</span> <span style="color: #888888">[FUNC]</span> </span><span>| Info from function
    </pre></div>
    </div>

Common mistakes
"""""""""""""""""
Please beware that if you have something like this in one of your files:

.. code-block:: python
    :caption: database_module.py

    from cliasi import Cliasi

    cli = Cliasi("DB")
    def initialize_database():
        pass

And maybe get the verbosity level from some config file / as arguments
and set the level after importing the module like this:

.. code-block:: python
    :caption: main_program.py

    from cliasi import cli
    from databasee_module import initialize_database

    def main():
        cli.min_verbose_level = 2  # Only warnings and errors
        initialize_database()

The Cliasi instance in database **will not infer** the verbosity level from the global instance
as it is created before the global instance's verbosity level is set.

To avoid this, either set the verbosity level before importing any modules that create their own Cliasi instances
or create Cliasi instances only in functions / after the global instance's settings are done.

Below are fixed versions of the above code snippets:

.. code-block:: python
    :caption: main_program_fixed.py

    from cliasi import cli

    def main():
        cli.min_verbose_level = 2  # Only warnings and errors
        from databasee_module import initialize_database
        initialize_database()

.. code-block:: python
    :caption: database_module_fixed.py

    from cliasi import Cliasi

    cli: Cliasi

    def initialize_database():
        cli = Cliasi("DB")
        pass