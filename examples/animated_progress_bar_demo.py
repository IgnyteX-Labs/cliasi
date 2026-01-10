import time

from cliasi import cli

task = cli.progressbar_animated_download(
    "Downloading",
)
for i in range(100):
    time.sleep(0.05)  # Simulate work
    task.update(progress=i)  # Update progress by 1
task.stop()  # Finish the progress bar
cli.success("Download complete.")
