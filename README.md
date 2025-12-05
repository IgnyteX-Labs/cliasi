# cliasi (cli easy)
Output pretty command line text without hassle.
<br>This is mostly a collection of pretty print commands

View the [documentation here](https://ignytex-labs.github.io/cliasi/).
### Installation
```shell
pip install cliasi
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

# You can even ask for input and the input will disappear
cli.log("Got input: " + cli.ask("Give input: "))
# > LOG [CLI] | Got input: test
```

### Prefix and Cliasi instances
Sometimes you might want to indicate different parts of your program working.<br>
You can do that by having another instance of Cliasi with another prefix

```python
from cliasi import cli, Cliasi  # Default shared Cliasi instance

cli.update_prefix("MANAGE")
cli.fail("Management failed")
# > X [MANAGE] | Management failed

def calculate():
    # Another part of your program could have its own instance
    clisi = Cliasi("CALC", use_oneline=True)
    clisi.info("Calculating...")
    # > i [CALC] | Calculating...
    # Although it might be better to use other methods for waiting
```

### Animations
Some processes might take a few seconds to complete and you dont know how much the process is done (you cant use a progress bar) <br>
In that case you can use either a blocking or non blocking animate method.

```python
from cliasi import cli

# This will wait for three seconds and display an animation
cli.animate_message_blocking("Saving files, press CRTL-C to stop", 3)
save_data()

# But if you want to wait for something to finish and display something nice in the meantime
task = cli.animate_message_non_blocking("Waiting for a process to quit")
# Put your processing logic here
do_stuff_that_takes_time()
task.stop()  # Stop the animation
cli.success("Process quit")
```
![animate_message_nonblocking look in the console](https://github.com/user-attachments/assets/e452fbbc-3eed-42c2-b05d-8f532ca11276)


### Progress Bars
You can also have a progress bar which adapts to the size of your terminal <br>
This is the "static" version which you just call whenever you get an update.

```python
from cliasi import cli

processed, total = 0, len(calculate_queue)
while not calculate_queue.is_empty():
    cli.progressbar("Calculating items...", processed / total)
    calculate_next_item()
    processed += 1

cli.success("Calculation complete")
# This will show a progress bar that will only update when a calculation has finished.
# Potentially bad if it gets stuck on a calculation
```
Or if you want to have the bar be animated while waiting for progress

```python
from cliasi import cli

task = cli.progressbar_animated_download("Downloading files.")
download()
task.update(10)
# You can also change the message while in the process
task._message = "Extracting"
extract()
task.update(40)
extract_again()

task.stop()
```
![progressbar_animated_download look in the console](https://github.com/user-attachments/assets/348ddfd8-f1ea-441d-873e-a17e6818fff5)
