from cliasi import Cliasi, cli


def function_that_has_no_idea_about_main_program():
    # Create a new instance with its own prefix
    local_cli = Cliasi(prefix="FUNC")
    local_cli.log("Debug will be shown as min verbosity is inferred by default")
    local_cli.info("Info from function")


cli.min_verbose_level = 0
cli.set_prefix("MAIN")
cli.log("Shown as min verbosity is DEBUG")
function_that_has_no_idea_about_main_program()
