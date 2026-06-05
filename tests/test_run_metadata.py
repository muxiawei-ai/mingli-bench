import unittest

from mingli_bench.run_metadata import build_run_metadata


class RunMetadataTests(unittest.TestCase):
    def test_build_run_metadata_has_reproducibility_keys(self):
        metadata = build_run_metadata()

        self.assertIn("git_commit", metadata)
        self.assertIn("git_dirty", metadata)
        self.assertIn("python_version", metadata)
        self.assertIn("platform", metadata)


if __name__ == "__main__":
    unittest.main()
