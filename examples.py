"""Test output of all methods"""
from cliasi import cli, Cliasi, TextColor
from time import sleep

cli.set_prefix("COLORS")
cli.message("LISTING COLORS")
for color in TextColor:
    cli.list(color.value + color.name)

cli.newline()
cli.set_prefix("STATIC")
cli.message("MESSAGE TEST")
cli.info("INFO TEST")
cli.log("LOG TEST")
cli.log_small("LOG SMALL TEST")
cli.list("STATIC LIST")
cli.warn("WARN TEST")
cli.fail("FAIL TEST")
cli.success("SUCCESS TEST")
cli.newline()

cli.set_prefix("LINEBREAKS")
cli.message("LINEBREAK TEST\nSUCCESSFUL")
cli.info("TEST THISWILLNOTBECUTOFF!" * 100)


cli.set_prefix("ANIMATED")
cli.animate_message_blocking("MESSAGE BLOCKING", 3)
task: Cliasi.NonBlockingProgressTask = cli.animate_message_non_blocking("MESSAGE NONBLOCKING")
sleep(3)
task.stop()
task: Cliasi.NonBlockingProgressTask = cli.animate_message_download_non_blocking("MESSAGE DOWNLOAD NONBLOCKING")
sleep(3)
task.stop()

cli.set_prefix("PROGRESS")
cli.newline()
cli.progressbar("PROGRESS", progress=70, override_messages_stay_in_one_line=False, show_percent=True)
cli.progressbar_download("PROGRESS DOWNLOAD", progress=70, override_messages_stay_in_one_line=False)
task = cli.progressbar_animated_normal("PROGRESS ANIMATED", progress=10, override_messages_stay_in_one_line=False, unicorn=True)
sleep(1)
task.update(progress=10)
sleep(1)
task.update(progress=1000)
sleep(1)
task.stop()
task = cli.progressbar_animated_download("PROGRESS ANIMATED DOWNLOAD", progress=10, override_messages_stay_in_one_line=False, show_percent=True, unicorn=True, interval=0.05)
sleep(1)
task.update(progress=10)
sleep(1)
task.update(progress=1000)
sleep(1)
task.stop()

cli.set_prefix("ASK")
cli.newline()

cli.ask("QUESTION: ")
result = cli.ask("HIDDEN: ", hide_input=True)
cli.info("RESULT: " + result)
