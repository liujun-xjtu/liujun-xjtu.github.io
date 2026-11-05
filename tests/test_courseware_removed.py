import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVED_SOURCES = (
    "data/nlp.yaml",
    "layouts/partials/home/zh-courses.html",
    "content/zh/teaching/_index.md",
    "content/en/teaching/_index.md",
)


class CoursewareRemovalTest(unittest.TestCase):
    def test_courseware_sources_are_removed(self):
        for relative_path in REMOVED_SOURCES:
            self.assertFalse((ROOT / relative_path).exists(), relative_path)

    def test_tracked_source_has_no_courseware_links_or_slides_module(self):
        for needle in ("jianguoyun" + ".com", "modules/" + "slides", "course_" + "enabled"):
            result = subprocess.run(
                ["git", "grep", "-l", needle, "--", ".", ":!tests/*"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode, result.stdout)

    def test_teaching_routes_and_navigation_are_removed(self):
        with tempfile.TemporaryDirectory() as destination:
            subprocess.run(["hugo", "--quiet", "--destination", destination], cwd=ROOT, check=True)
            site = Path(destination)
            self.assertFalse((site / "zh" / "teaching").exists())
            self.assertFalse((site / "en" / "teaching").exists())
            zh_home = (site / "zh" / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("讲授课程", zh_home)


if __name__ == "__main__":
    unittest.main()
