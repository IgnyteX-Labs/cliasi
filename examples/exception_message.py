# cliasi needs to be imported to intercept exceptions
# noinspection PyUnusedImports
# ruff: noqa: F401
import cliasi

# Importing cliasi automatically installs the logging handler
raise ValueError("An example error")
