"""Quick verification of ML artifacts."""

import json
import os

import numpy as np
import onnxruntime as ort

# === categorizer.onnx ===
print("=== categorizer.onnx ===")
session = ort.InferenceSession("ml/models/categorizer.onnx")
for inp in session.get_inputs():
    print(f"  Input: {inp.name} shape={inp.shape} type={inp.type}")
for out in session.get_outputs():
    print(f"  Output: {out.name} shape={out.shape} type={out.type}")

size_mb = os.path.getsize("ml/models/categorizer.onnx") / 1024 / 1024
print(f"  Size: {size_mb:.1f} MB")

dummy_ids = np.zeros((1, 64), dtype=np.int64)
dummy_mask = np.ones((1, 64), dtype=np.int64)
logits = session.run(None, {"input_ids": dummy_ids, "attention_mask": dummy_mask})[0]
preds = int(np.argmax(logits, axis=-1)[0])

with open("ml/models/label_encoder.json") as f:
    enc = json.load(f)
print(f"  Sample prediction: {enc['id2label'][str(preds)]}")
print(f"  Logits shape: {logits.shape}")
print(f"  num_labels: {enc['num_labels']}")

# === tokenizer ===
print("\n=== tokenizer/ ===")
for fn in os.listdir("ml/models/tokenizer"):
    sz = os.path.getsize(f"ml/models/tokenizer/{fn}") / 1024
    print(f"  {fn} ({sz:.1f} KB)")

# === xgboost_spending.onnx ===
print("\n=== xgboost_spending.onnx ===")
xgb = ort.InferenceSession("ml/models/xgboost_spending.onnx")
size_kb = os.path.getsize("ml/models/xgboost_spending.onnx") / 1024
print(f"  Size: {size_kb:.1f} KB")

print("\n✅ All artifacts verified successfully")
