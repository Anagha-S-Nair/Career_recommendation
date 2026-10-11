"""
Model Loader Module.
Loads and caches serialized production ML models and preprocessors.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODELS_DIR = Path(__file__).resolve().parent / "models"


class ModelArtifactError(Exception):
    """Raised when model artifacts cannot be loaded or paths are invalid."""
    pass


class ModelLoader:
    """Manages loading, caching, and introspection of production ML models."""
    _instance: Optional["ModelLoader"] = None
    _model: Optional[Any] = None
    _preprocessor: Optional[Any] = None
    _config: Optional[Dict[str, Any]] = None
    _metadata: Optional[Dict[str, Any]] = None
    _version: Optional[Dict[str, Any]] = None

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = Path(model_dir) if model_dir else DEFAULT_MODELS_DIR

    @classmethod
    def get_instance(cls, model_dir: Optional[Path] = None) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = cls(model_dir)
        return cls._instance

    def is_loaded(self) -> bool:
        return self._model is not None and self._preprocessor is not None

    def load(self, force_reload: bool = False) -> Dict[str, Any]:
        """Instance method to load and validate artifacts in self.model_dir."""
        if not self.model_dir.exists() or not self.model_dir.is_dir():
            raise ModelArtifactError(f"Model directory does not exist or is invalid: {self.model_dir}")

        model_file = self.model_dir / "model.joblib"
        prep_file = self.model_dir / "preprocessor.joblib"

        if not model_file.exists():
            raise ModelArtifactError(f"Champion model missing at {model_file}")
        if not prep_file.exists():
            raise ModelArtifactError(f"Preprocessor missing at {prep_file}")

        try:
            model = joblib.load(model_file)
            prep = joblib.load(prep_file)
            self._model = model
            self._preprocessor = prep
            ModelLoader._model = model
            ModelLoader._preprocessor = prep
            return {'model': model, 'preprocessor': prep}
        except Exception as e:
            raise ModelArtifactError(f"Failed to load artifacts: {str(e)}") from e

    @classmethod
    def get_model(cls) -> Any:
        if cls._model is None:
            loader = cls.get_instance(DEFAULT_MODELS_DIR)
            artifacts = loader.load()
            cls._model = artifacts['model']
            cls._preprocessor = artifacts['preprocessor']
            logger.info("Loaded champion model into memory.")
        return cls._model

    @classmethod
    def get_preprocessor(cls) -> Any:
        if cls._preprocessor is None:
            cls.get_model()
        return cls._preprocessor

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        if cls._config is None:
            cfg_path = DEFAULT_MODELS_DIR / "model_config.json"
            if cfg_path.exists():
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cls._config = json.load(f)
            else:
                cls._config = {"model": "RandomForest", "threshold": 0.5, "confidence_margin": 0.27}
        return cls._config

    @classmethod
    def get_model_metadata(cls) -> Dict[str, Any]:
        if cls._metadata is None:
            meta_path = DEFAULT_MODELS_DIR / "model_metadata.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    cls._metadata = json.load(f)
            else:
                cls._metadata = {"model_name": "PathFinder Career Compatibility Classifier"}
        return cls._metadata

    @classmethod
    def get_model_version(cls) -> Dict[str, Any]:
        if cls._version is None:
            ver_path = DEFAULT_MODELS_DIR / "version.json"
            if ver_path.exists():
                with open(ver_path, "r", encoding="utf-8") as f:
                    cls._version = json.load(f)
            else:
                cls._version = {"version": "V13.0-RandomForest-Champion-Benchmark"}
        return cls._version

    @classmethod
    def is_model_ready(cls) -> bool:
        try:
            cls.get_model()
            cls.get_preprocessor()
            return True
        except Exception:
            return False


def get_model() -> Any:
    return ModelLoader.get_model()


def get_preprocessor() -> Any:
    return ModelLoader.get_preprocessor()


def get_model_config() -> Dict[str, Any]:
    return ModelLoader.get_model_config()


def get_model_metadata() -> Dict[str, Any]:
    return ModelLoader.get_model_metadata()


def get_model_version() -> Dict[str, Any]:
    return ModelLoader.get_model_version()


def get_feature_columns() -> List[str]:
    return [
        'age', 'class', 'ability_match_component', 'interest_match_component',
        'academic_match_component', 'learning_match_component', 'composite_alignment_index',
        'ability_interest_synergy', 'ability_interest_gap', 'min_core_match',
        'max_core_match', 'harmonic_core_match', 'geometric_core_synergy', 'holistic_synergy',
        'stream', 'career_domain', 'career_name'
    ]


def get_classes() -> Dict[str, Any]:
    return {'classes': [0, 1]}


def is_model_ready() -> bool:
    return ModelLoader.is_model_ready()

