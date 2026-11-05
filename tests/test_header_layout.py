import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALIGNMENT_RULE = "#site-header .navbar{padding-left:max(3.5rem,calc((100% - 1200px)/2 + 3.5rem))}"


class HeaderLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        subprocess.run(["hugo", "--quiet", "--destination", cls._tmp.name], cwd=ROOT, check=True)
        cls.zh_home = (Path(cls._tmp.name) / "zh" / "index.html").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_title_uses_profile_photo_left_alignment(self):
        self.assertIn(ALIGNMENT_RULE, self.zh_home)

    def test_theme_toggle_is_not_rendered(self):
        self.assertNotIn('class="theme-toggle', self.zh_home)
        self.assertNotIn('id="moon"', self.zh_home)
        self.assertNotIn('id="sun"', self.zh_home)


if __name__ == "__main__":
    unittest.main()
