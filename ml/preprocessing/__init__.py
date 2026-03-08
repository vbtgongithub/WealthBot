"""
WealthBot ML Preprocessing Module
Feature engineering and data transformation.
"""

from ml.preprocessing.features import (
    build_training_matrix,
    extract_user_features,
    load_feature_config,
)
from ml.preprocessing.synthetic_data import generate_synthetic_dataset

__all__ = [
    "build_training_matrix",
    "extract_user_features",
    "generate_synthetic_dataset",
    "load_feature_config",
]
