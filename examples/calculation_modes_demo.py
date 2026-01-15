from time import sleep

from cliasi import PBCalculationMode, cli

for i in range(100):
    sleep(0.025)
    # Fills across the full width but skips text
    cli.progressbar(
        "progress goes",
        message_right="under text",
        progress=i,
        calculation_mode=PBCalculationMode.FULL_WIDTH,
        show_percent=True,
    )

for i in range(100):
    sleep(0.025)
    # Fills only empty space between text segments
    cli.progressbar_download(
        message_left="progress goes between here",
        message_right="and there",
        progress=i,
        calculation_mode=PBCalculationMode.ONLY_EMPTY,
    )

for i in range(100):
    sleep(0.025)
    # Overwrites text when the bar reaches it (useful for dense bars)
    cli.progressbar(
        message_left=None,
        message_right="This text will be overwritten",
        progress=i,
        calculation_mode=PBCalculationMode.FULL_WIDTH_OVERWRITE,
    )
