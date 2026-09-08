"""
build_block.py
----------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 build_block.py
"""

import json

from block import Block
from lab_utils import ask, title

title("Montando um bloco na mão")

transacao = ask(
    "Digite uma transação de exemplo para colocar no bloco",
    "Alice paga 5 moedas para Bob",
)

b = Block(index=1, transactions=[transacao], previous_hash="0" * 64)

print(f"\n  Hash calculado sobre esse conteúdo (SHA-256):\n  {b.hash}")

with open("bloco_exemplo.json", "w", encoding="utf-8") as f:
    json.dump(b.to_dict(), f, indent=2, ensure_ascii=False, default=str)
print("\n  (Esse bloco foi salvo em bloco_exemplo.json — abra o arquivo para inspecionar.)")
