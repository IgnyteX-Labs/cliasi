from time import sleep

from cliasi import Cliasi

cli = Cliasi(min_verbose_level=20, messages_stay_in_one_line=True, colors=True)
cli.success("Installation successful!")
cli.set_prefix("hobby_app")
progressbar = cli.progressbar_animated_download("Downloading...", show_percent=True)
# Do some downloading work here...
for i in range(70):
    sleep(0.05)  # originally do_something()
    progressbar.update(progress=i)
sleep(0.05 * 30)  # originally do_task_that_takes_long_time()
progressbar.update(progress=100)
# Finish download
sleep(1)  # originally clean_up()
progressbar.stop()
cli.success("Download complete!", message_right="100%")
