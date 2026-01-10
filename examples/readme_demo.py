# File: examples/readme_demo.py
from time import sleep

from cliasi import cli

# This will wait for three seconds and display an animation
task = cli.animate_message_non_blocking("Saving files, press CRTL-C to stop")
sleep(2)  # originally do_stuff()
task.update("Files saved, waiting for process to quit")
sleep(2.5)  # originally tell_process_to_quit()
task.stop()
cli.success("Process quit")
