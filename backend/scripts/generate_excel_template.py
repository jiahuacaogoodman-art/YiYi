from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.import_service import generate_template


if __name__ == "__main__":
    path = generate_template()
    print(f"Excel 模板已生成：{path}")
