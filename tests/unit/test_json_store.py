from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from todolite.infrastructure.json_store import JsonStore


class JsonStoreTests(unittest.TestCase):
    def test_atomic_save_and_corrupt_file_fallback(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "data.json"
            JsonStore.save(path, {"value": 1})
            self.assertEqual(JsonStore.load(path, {}), {"value": 1})
            path.write_text("{broken", encoding="utf-8")
            self.assertEqual(JsonStore.load(path, {"fallback": True}), {"fallback": True})


if __name__ == "__main__":
    unittest.main()
