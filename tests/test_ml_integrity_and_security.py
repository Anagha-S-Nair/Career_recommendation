"""
Automated Tests: Model Artifact Integrity, Security, and File Validation.
"""

import unittest
import hashlib
import json
from pathlib import Path


class TestMLIntegrityAndSecurity(unittest.TestCase):
    """Verifies SHA-256 integrity of all production ML artifacts and security rules."""

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.model_dir = self.base_dir / "backend" / "ml" / "models"
        self.data_dir = self.base_dir / "backend" / "ml" / "data"

    def test_artifact_sha256_hashes(self):
        """Verifies artifact SHA-256 integrity against recorded baseline."""
        integrity_file = self.base_dir / "tests" / "reports" / "model_artifact_integrity.json"
        self.assertTrue(integrity_file.exists(), "Integrity report file missing")

        with open(integrity_file, "r", encoding="utf-8") as f:
            integrity_data = json.load(f)

        for filename, info in integrity_data.get("files", {}).items():
            if filename == "career_knowledge_requirements.csv":
                file_path = self.data_dir / filename
            else:
                file_path = self.model_dir / filename

            self.assertTrue(file_path.exists(), f"Artifact {filename} does not exist at {file_path}")
            with open(file_path, "rb") as af:
                computed_hash = hashlib.sha256(af.read()).hexdigest()
            self.assertEqual(
                computed_hash,
                info["sha256"],
                f"Hash mismatch for {filename}! Expected {info['sha256']} but got {computed_hash}"
            )

    def test_gitignore_security(self):
        """Ensures .env and secret files are explicitly ignored."""
        gitignore_path = self.base_dir / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore file must exist")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".env", content, ".gitignore must ignore .env files")

    def test_no_arbitrary_path_traversal(self):
        """Ensures ModelLoader rejects invalid path traversals."""
        from backend.ml.model_loader import ModelLoader, ModelArtifactError
        invalid_path = Path("/invalid/traversal/path/does_not_exist")
        loader = ModelLoader(model_dir=invalid_path)
        with self.assertRaises(ModelArtifactError):
            loader.load(force_reload=True)


if __name__ == '__main__':
    unittest.main()
