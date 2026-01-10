import unittest
from unittest.mock import patch

from cliasi.cliasi import Cliasi


class TestAnimationFallbacks(unittest.TestCase):
    def setUp(self):
        self.cli = Cliasi()
        # Mock cliasi.ANIMATIONS_MAIN directly since it was imported as a reference
        self.cli_animations_patcher = patch("cliasi.cliasi.ANIMATIONS_MAIN")
        self.mock_animations = self.cli_animations_patcher.start()

        self.warn_patcher = patch.object(Cliasi, "warn")
        self.mock_warn = self.warn_patcher.start()

        # Mock print to avoid cluttering test output
        self.print_patcher = patch("builtins.print")
        self.mock_print = self.print_patcher.start()

    def tearDown(self):
        self.cli_animations_patcher.stop()
        self.warn_patcher.stop()
        self.print_patcher.stop()

    def test_animate_message_blocking_fallback_frames(self):
        # We use a malformed entry
        self.mock_animations.__getitem__.return_value = {
            "frames": "not a list",
            "frame_every": 1,
        }
        self.mock_animations.__len__.return_value = 1

        # This should call self.warn
        self.cli.animate_message_blocking("test", time=0.1, interval=0.05)

        self.mock_warn.assert_any_call(
            "CLIASI error: "
            "Animation frames must be a list, got str."
            " Falling back to default frames.",
            override_messages_stay_in_one_line=False,
        )

    def test_animate_message_blocking_fallback_frame_every(self):
        self.mock_animations.__getitem__.return_value = {
            "frames": ["frame1"],
            "frame_every": "not an int",
        }
        self.mock_animations.__len__.return_value = 1

        self.cli.animate_message_blocking("test", time=0.1, interval=0.05)

        self.mock_warn.assert_any_call(
            "CLIASI error: frame_every must be an int, got str. Falling back to 1.",
            override_messages_stay_in_one_line=False,
        )

    def test_non_blocking_animation_fallback_frames(self):
        # For non-blocking, we pass the animation dict directly to __get_animation_task
        malformed_animation = {"frames": None, "frame_every": 1}
        self.mock_animations.__getitem__.return_value = malformed_animation
        self.mock_animations.__len__.return_value = 1

        task = self.cli.animate_message_non_blocking("test", interval=0.1)
        if task:
            # The warning happens inside the update() which is called by the thread.
            # However, task.update() also calls it.
            task.update()
            task.stop()

        self.mock_warn.assert_any_call(
            "CLIASI error: "
            "Animation frames must be a list, got NoneType."
            " Falling back to default frames.",
            override_messages_stay_in_one_line=False,
        )


if __name__ == "__main__":
    unittest.main()
