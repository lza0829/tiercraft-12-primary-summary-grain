import os
import tempfile
from pathlib import Path

# 必须在任何 app.* 导入前指定独立测试库目录
_TMP = Path(tempfile.mkdtemp(prefix="tiercraft-test-"))
os.environ.setdefault("DATA_DIR", str(_TMP))
os.environ.setdefault(
    "FIXTURES_DIR", str(Path(__file__).resolve().parents[2] / "fixtures")
)
