"""Atalho: roda o pipeline inteiro (coletar -> processar -> gerar site).

Uso:  python src/atualizar.py

É o mesmo comando que o GitHub Actions vai rodar de hora em hora (Fase 4).
"""
import subprocess
import sys
from pathlib import Path

PASTA_SRC = Path(__file__).resolve().parent

# (script, argumentos). processar usa 7 dias para o Top 5 da semana enxergar a semana toda.
# kit.py --so-site só atualiza o site (os arquivos em content/ você gera quando quiser: python src/kit.py).
PASSOS = [("coletar.py", []), ("processar.py", ["--dias", "7"]),
          ("gerar_site.py", []), ("kit.py", ["--so-site"])]

for script, argumentos in PASSOS:
    print(f"\n=== {script} ===")
    # Usa o mesmo Python que está rodando este arquivo (o do .venv).
    resultado = subprocess.run([sys.executable, str(PASTA_SRC / script), *argumentos])
    if resultado.returncode != 0:
        sys.exit(f"Falhou em {script}. Corrija o erro acima e rode de novo.")
print("\nPronto! Abra site/index.html no navegador.")
