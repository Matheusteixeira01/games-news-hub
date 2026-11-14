"""Atalho: roda o pipeline inteiro (coletar -> processar -> gerar site).

Uso:  python src/atualizar.py

É o mesmo comando que o GitHub Actions vai rodar de hora em hora (Fase 4).
"""
import subprocess
import sys
from pathlib import Path

PASTA_SRC = Path(__file__).resolve().parent

for script in ["coletar.py", "processar.py", "gerar_site.py"]:
    print(f"\n=== {script} ===")
    # Usa o mesmo Python que está rodando este arquivo (o do .venv).
    resultado = subprocess.run([sys.executable, str(PASTA_SRC / script)])
    if resultado.returncode != 0:
        sys.exit(f"Falhou em {script}. Corrija o erro acima e rode de novo.")
print("\nPronto! Abra site/index.html no navegador.")
