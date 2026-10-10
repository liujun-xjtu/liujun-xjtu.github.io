import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_TITLE = "从大模型到教学智能体：能力失配与技术展望"
PAPER_SLUG = "从大模型到教学智能体能力失配与技术展望"


class NewContentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        subprocess.run(
            ["hugo", "--quiet", "--destination", cls._tmp.name],
            cwd=ROOT,
            check=True,
        )
        cls.zh_research = (Path(cls._tmp.name) / "zh" / "research" / "index.html").read_text(encoding="utf-8")
        cls.en_home = (Path(cls._tmp.name) / "en" / "index.html").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_requested_papers_are_rendered(self):
        self.assertIn(PAPER_TITLE, self.zh_research)
        self.assertIn("教育智能化前沿, 2026, 39(02):21-31", self.zh_research)
        self.assertIn("CoLM 2026", self.zh_research)

    def test_chinese_article_is_grouped_as_journal(self):
        title_at = self.zh_research.index(PAPER_TITLE)
        separator_at = self.zh_research.rfind("pub-sep-", 0, title_at)
        self.assertEqual("j", self.zh_research[separator_at + len("pub-sep-")])

    def test_publication_pages_and_bibtex_exist_in_both_languages(self):
        for language in ("en", "zh"):
            publication = ROOT / "content" / language / "publication" / PAPER_SLUG
            self.assertTrue((publication / "index.md").is_file())
            self.assertIn(PAPER_TITLE, (publication / "index.md").read_text(encoding="utf-8"))
            self.assertTrue((publication / "cite.bib").is_file())

    def test_project_is_rendered_in_both_languages(self):
        self.assertIn("国家自然科学基金卓越研究群体项目", self.zh_research)
        self.assertIn("机器记忆持续学习", self.zh_research)
        self.assertIn("Machine Memory Intelligence, NSFC Excellent Research Group Project", self.en_home)
        self.assertIn("Continual Learning for Machine Memory", self.en_home)


if __name__ == "__main__":
    unittest.main()
