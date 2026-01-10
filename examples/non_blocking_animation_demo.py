import time

from cliasi import cli

cli.messages_stay_in_one_line = True  # To hide animation after finished.
task = cli.animate_message_non_blocking("Processing...")
# Do other stuff while the animation is running
time.sleep(3)  # Simulate a long task
task.stop()  # Stop the animation when done
cli.success("Done!")
