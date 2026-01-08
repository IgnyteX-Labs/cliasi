from cliasi import cli

name = cli.ask("What is your name?")
code = cli.ask("Enter your secret code:", hide_input=True)

cli.info(f"Hello, {name} with code {code}")
