import contextlib
import io
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / "skills" / "reforma-tributaria"
EXEMPLOS = RAIZ / "examples"
sys.path.insert(0, str(SKILL / "scripts"))


def rodar(main, argv):
    """Executa main(argv) e devolve (codigo, stdout). SystemExit vira código."""
    out = io.StringIO()
    codigo = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        try:
            codigo = main(argv) or 0
        except SystemExit as e:
            codigo = e.code if isinstance(e.code, int) else 1
    return codigo, out.getvalue()


def rodar_json(main, argv):
    codigo, saida = rodar(main, argv + ["--json"])
    return codigo, json.loads(saida)
