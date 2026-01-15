# cliasi (cli easy)

![GitHub issues](https://img.shields.io/github/issues/IgnyteX-Labs/cliasi)
![PyPI](https://img.shields.io/pypi/v/cliasi)

Output pretty command line text without hassle.
<br>This is mostly a collection of pretty print commands

View the [documentation here](https://cliasi.readthedocs.io/).

### Installation
```shell
pip install cliasi
uv add cliasi
```

## Basic Usage

```python
from cliasi import cli

cli.success("It works!")
# > ✔ [CLI] | It works!

cli.messages_stay_in_one_line = True
# The next few lines will get overwritten
cli.info("blah")
cli.warn("doing something dangerous")
# > ! [CLI] | doing something dangerous
```

Read more about different message types and see visualizations in the documentation
[here](https://cliasi.readthedocs.io/en/latest/message_types.html).

### Animations

One of the main features of cliasi is the ability to display animations while waiting
for something to finish.

```python
# File: examples/readme_demo.py
from cliasi import cli

# This will wait for three seconds and display an animation
task = cli.animate_message_non_blocking(
    "Saving files...",
    message_right="[CTRL-C to abort]",
    messages_stay_in_one_line=True
)
do_stuff()
task.update("Files saved, waiting for process to quit", message_right="70%")
tell_process_to_quit()
task.stop()
cli.success("Process quit", message_right="100%")
```

![readme_demo](docs/source/_static/asciinema/readme_demo.gif)

### Catching exceptions

cliasi also catches exceptions and displays them in a pretty way.
This then looks something like this:

```python
# exception_message.py
import cliasi

# Importing cliasi automatically installs the logging handler
raise ValueError("An example error")
```

Example CLI output (uncolored,
see colored version in
[docs](https://cliasi.readthedocs.io/en/latest/message_types.html)):

```text
X [CLI] | Uncaught exception:
X [CLI] | Traceback (most recent call last):
        |   File "examples/exception_message.py", line 4, in <module>
        |     raise ValueError("An example error")
        | ValueError: An example error
```

### Other features

cliasi has many more features like:

- Logging integration
- Custom message alignments
- Customizable progressbars (with `PBCalculationMode`)
- And more!

### Contributing:

This is just a fun project of mine mainly to try out python packaging.
If you would like to contribute or have a feature-request,
please [open an issue or pull request](https://github.com/Qrashi/cliasi/issues/new).
