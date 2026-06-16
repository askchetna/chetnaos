"""One-shot: generate organ compat shims."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.chetnaos.organs import ORGAN_IMPORTS

root = ROOT / "src" / "chetnaos" / "organs"
for name, (mod, cls) in ORGAN_IMPORTS.items():
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    content = f'''"""{name} organ — v3 compat shim."""
from {mod} import {cls}

__all__ = ["{cls}"]
'''
    (d / "__init__.py").write_text(content, encoding="utf-8")
    print(f"  {name}")

print(f"Created {len(ORGAN_IMPORTS)} organ shims")
