from cliasi import cli

cli.info("This is a left-aligned message.")  # Default is left-aligned
cli.success("This is a right-aligned message.", message_right=True)
cli.warn(False, message_center="This is a centered message.")
# False because parameter message_left is required to be set. Can also use ""
cli.info("From left", message_center="to the middle", message_right="to the right")
