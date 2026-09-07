"""
check_validity.py
--------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 check_validity.py

Este script NÃO ataca nada — ele só faz uma coisa: carrega a cadeia
salva em disco e roda is_chain_valid() nela. É exatamente essa operação
que qualquer nó da rede executa, de forma independente, para conferir a
integridade da cadeia inteira sozinho.

Ele carrega cadeia_adulterada.json se esse arquivo existir (ou seja, se
você já rodou o tamper_attack.py); caso contrário, carrega
cadeia.json (a versão original, sem ataque nenhum).
"""

import os
import sys

from blockchain import Blockchain
from lab_utils import title

if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    arquivo = sys.argv[1]
elif os.path.exists("cadeia_adulterada.json"):
    arquivo = "cadeia_adulterada.json"
elif os.path.exists("cadeia.json"):
    arquivo = "cadeia.json"
else:
    sys.exit(
        "Nenhuma cadeia encontrada.\n"
        "Rode primeiro: python3 build_chain.py"
    )

title("Só a verificação: is_chain_valid()")

print(f"  Carregando {arquivo}...")
bc = Blockchain.load(arquivo)
print(f"  Cadeia carregada ({len(bc.chain)} blocos).")

print(
    "\n  Este comando não muda nada na cadeia — ele só confere. É o mesmo\n"
    "  código que qualquer participante da rede roda, de forma totalmente\n"
    "  independente, sem precisar confiar em quem propôs os blocos."
)

valido, problemas = bc.is_chain_valid()
print(f"\n  is_chain_valid() -> {valido}")
for p in problemas:
    print(f"    [DETECTADO] {p}")

if valido:
    print("\n  Nenhum problema encontrado — esta cadeia está íntegra.")
else:
    print(
        "\n  Dica: rode este comando de novo a qualquer momento — o resultado\n"
        "  é sempre determinístico a partir do que estiver salvo nos arquivos\n"
        "  .json. Ninguém precisa 'lembrar' se a cadeia é válida: dá para\n"
        "  recalcular do zero sempre que quiser."
    )
