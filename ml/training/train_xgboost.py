"""
WealthBot XGBoost Spending Predictor — Training Script
=======================================================
Trains an XGBoost regressor to predict **next-7-day spending** from the
21-feature vector defined in ``ml/models/feature_config.json``.

Designed to run standalone on **Google Colab (CPU)** or locally.

Outputs
-------
- ``ml/models/xgboost_spending.onnx`` — ONNX model for production inference
- Console metrics: MAE, RMSE, R², feature importances

Usage
-----
::

    # Local (from project root, venv activated)
    python -m ml.training.train_xgboost

    # Google Colab
    !pip install xgboost scikit-learn onnxmltools onnxruntime numpy
    # Upload X_train.npy / y_train.npy, then run this file
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from xgboost import XGBRegressor

# =============================================================================
# Paths
# =============================================================================

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
X_TRAIN_PATH = MODELS_DIR / "X_train.npy"
Y_TRAIN_PATH = MODELS_DIR / "y_train.npy"
FEATURE_CONFIG_PATH = MODELS_DIR / "feature_config.json"
ONNX_OUTPUT_PATH = MODELS_DIR / "xgboost_spending.onnx"


# =============================================================================
# Data Loading
# =============================================================================


def load_data() -> tuple[np.ndarray, np.ndarray]:
    """Load the pre-built training matrix from .npy files.

    Returns:
        Tuple of ``(X, y)`` arrays — float32, shapes (n, 21) and (n,).
    """
    X: np.ndarray = np.load(X_TRAIN_PATH)
    y: np.ndarray = np.load(Y_TRAIN_PATH)
    print(f"Loaded X: {X.shape}, y: {y.shape}")
    print(
        f"  y  mean={y.mean():.2f}  std={y.std():.2f}  "
        f"min={y.min():.2f}  max={y.max():.2f}"
    )
    return X, y


def load_feature_names() -> list[str]:
    """Load feature names from the config JSON."""
    with open(FEATURE_CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    return [feat["name"] for feat in config["features"]]


# =============================================================================
# Time-aware Train/Test Split
# =============================================================================


def time_aware_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data chronologically — first 80% train, last 20% test.

    The training matrix from ``build_training_matrix()`` is ordered by
    (user, snapshot_date), so a simple positional split preserves
    temporal ordering within each user.

    Args:
        X: Feature matrix (n, 21).
        y: Target vector (n,).
        train_ratio: Fraction for training set.

    Returns:
        (X_train, X_test, y_train, y_test) tuple.
    """
    split_idx = int(len(X) * train_ratio)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    print(f"Train: {X_train.shape[0]} samples  |  Test: {X_test.shape[0]} samples")
    return X_train, X_test, y_train, y_test


# =============================================================================
# Model Training
# =============================================================================


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> XGBRegressor:
    """Train the XGBoost regressor with early stopping.

    Args:
        X_train: Training features.
        y_train: Training targets.
        X_test: Validation features.
        y_test: Validation targets.

    Returns:
        Fitted ``XGBRegressor`` instance.
    """
    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        tree_method="hist",
        early_stopping_rounds=20,
        eval_metric="rmse",
    )

    print("\nTraining XGBRegressor (n_estimators=200, max_depth=6, lr=0.1)...")
    start = time.perf_counter()

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=20,
    )

    elapsed = time.perf_counter() - start
    print(
        f"Training completed in {elapsed:.1f}s "
        f"(best iteration: {model.best_iteration})"
    )
    return model


# =============================================================================
# Evaluation
# =============================================================================


def evaluate(
    model: XGBRegressor,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: list[str],
) -> dict[str, float]:
    """Evaluate model and print metrics + top feature importances.

    Args:
        model: Trained XGBRegressor.
        X_test: Test features.
        y_test: Test targets.
        feature_names: Names for each feature column.

    Returns:
        Dict with MAE, RMSE, R² metrics.
    """
    y_pred: np.ndarray = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(root_mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    print("\n" + "=" * 50)
    print("Test Set Metrics")
    print("=" * 50)
    print(f"  MAE:  ₹{mae:,.2f}")
    print(f"  RMSE: ₹{rmse:,.2f}")
    print(f"  R²:   {r2:.4f}")

    # Feature importances (gain-based)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    print("\nTop 10 Feature Importances (gain):")
    for rank, idx in enumerate(indices[:10], 1):
        name = feature_names[idx] if idx < len(feature_names) else f"f{idx}"
        print(f"  {rank:2d}. {name:<30s}  {importances[idx]:.4f}")

    return {"mae": mae, "rmse": rmse, "r2": r2}


# =============================================================================
# ONNX Export
# =============================================================================


def export_onnx(model: XGBRegressor, n_features: int = 21) -> None:
    """Export the trained model to ONNX format.

    Args:
        model: Trained XGBRegressor.
        n_features: Number of input features.
    """
    # onnxmltools handles XGBoost → ONNX conversion
    from onnxmltools import convert_xgboost
    from onnxmltools.convert.common.data_types import FloatTensorType

    print(f"\nExporting to ONNX → {ONNX_OUTPUT_PATH}")

    initial_types = [("input", FloatTensorType([None, n_features]))]
    onnx_model = convert_xgboost(model, initial_types=initial_types)

    with open(ONNX_OUTPUT_PATH, "wb") as f:
        f.write(onnx_model.SerializeToString())

    # Verify the ONNX model loads and produces same output
    _verify_onnx(model, n_features)

    print(f"ONNX model saved ({ONNX_OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")


def _verify_onnx(model: XGBRegressor, n_features: int) -> None:
    """Verify ONNX output matches XGBoost output."""
    import onnxruntime as ort

    session = ort.InferenceSession(str(ONNX_OUTPUT_PATH))
    test_input = (
        np.random.default_rng(0).standard_normal((5, n_features)).astype(np.float32)
    )

    xgb_pred = model.predict(test_input)
    onnx_pred = session.run(None, {"input": test_input})[0].flatten()

    max_diff = float(np.max(np.abs(xgb_pred - onnx_pred)))
    print(f"ONNX verification — max abs diff: {max_diff:.6f}", end="")
    if max_diff < 0.01:
        print(" ✓")
    else:
        print(" ✗ (WARN: diff exceeds 0.01)")


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    """Run the full training pipeline."""
    print("=" * 60)
    print("WealthBot — XGBoost Spending Predictor Training")
    print("=" * 60)

    X, y = load_data()
    feature_names = load_feature_names()

    X_train, X_test, y_train, y_test = time_aware_split(X, y, train_ratio=0.8)

    model = train_model(X_train, y_train, X_test, y_test)
    evaluate(model, X_test, y_test, feature_names)
    export_onnx(model, n_features=X.shape[1])

    print("\n✅ Training pipeline complete.")


if __name__ == "__main__":
    main()
