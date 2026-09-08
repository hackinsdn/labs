"""
tamper_fix_attempt.py
------------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 tamper_fix_attempt.py

Pré-requisito: rode antes o tamper_attack.py (ele cria os arquivos
cadeia_adulterada.json e ataque_info.json que este script carrega).
"""

import json
import os
import sys

from blockchain import Blockchain
from lab_utils import title

if not os.path.exists("cadeia_adulterada.json") or not os.path.exists("ataque_info.json"):
    sys.exit(
        "Arquivos de estado não encontrados.\n"
        "Rode primeiro: python3 tamper_attack.py"
    )

title("Por que não basta 'corrigir' o hash?")

bc = Blockchain.load("cadeia_adulterada.json")
with open("ataque_info.json", encoding="utf-8") as f:
    idx = json.load(f)["indice_atacado"]

print(
    "Você pode pensar: 'o atacante só precisa recalcular o hash certo\n"
    "depois de mudar os dados'. Vamos ver o que acontece se ele tentar\n"
    "exatamente isso (sem re-minerar, ou seja, sem redescobrir um nonce\n"
    "que respeite a dificuldade de Proof of Work)."
)

print("\nAlterações:")

print(f"  Hash Antigo: {bc.chain[idx].hash}")
print(f"  Hash Novo: {bc.chain[idx].compute_hash()}")

bc.chain[idx].hash = bc.chain[idx].compute_hash()

bc.save("cadeia_adulterada2.json")
print("\nBlockchain salva em cadeia_adulterada2.json")
