.. _instances:

Cliasi instances
==================

Having multiple cliasi instances allows you to easily
communicate different program scopes.

Part A of your program has one instance with its own prefix
while part B has another instance with a different prefix.

.. code-block:: python
    :caption: :attr:`~cliasi.Cliasi.min_verbose_level` is inferred from global instance if not set.

    from cliasi import Cliasi

    def function_that_has_no_idea_about_main_program():
        # Create a new instance with its own prefix
        local_cli = Cliasi(prefix="FUNC")
        local_cli.debug("Debug will be shown as min verbosity is inferred by default")
        local_cli.info("Info from function")

    cli = Cliasi(prefix="MAIN", min_verbose_level=0)
    cli.debug("Shown as min verbosity is DEBUG")
