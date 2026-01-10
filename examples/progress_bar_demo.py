import time

from cliasi import cli

for i in range(101):
    cli.progressbar("Calculating", progress=i, show_percent=True)
    time.sleep(0.02)
cli.newline()  # Add a newline after the progress bar is complete
cli.success("Calculation complete.")
# Use cli.progressbar_download() for download-style progress bars.
