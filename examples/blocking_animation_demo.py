from cliasi import cli

cli.animate_message_blocking("Saving...", time=3, message_right="[CTRL-C] to stop")
# You cant do anything else while the animation is running
# Useful if you save something to a file at the end of a program
# User can CTRL-C while this is running
cli.success("Data saved!")
