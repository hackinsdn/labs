"""
sign_transaction.py
----------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 sign_transaction.py

Pré-requisito: rode antes o create_wallet.py (ele cria os
arquivos carteira_alice.json e carteira_bob.json que este script
carrega). Salva o resultado em transacao.json.
"""

import os
import sys

from wallet import Wallet, Transaction
from lab_utils import ask, title

if not os.path.exists("carteira_alice.json") or not os.path.exists("carteira_bob.json"):
    sys.exit(
        "Arquivos de carteira não encontrados.\n"
        "Rode primeiro: python3 create_wallet.py"
    )

title("Criando e assinando uma transação")

alice = Wallet.load("carteira_alice.json")
bob = Wallet.load("carteira_bob.json")
print("  Carteiras da Alice e do Bob carregadas.")

valor_str = ask("Quantas moedas a Alice vai enviar para o Bob?", "10")
try:
    valor = float(valor_str)
except ValueError:
    valor = 10

tx = Transaction(sender_address=alice.address, recipient_address=bob.address, amount=valor)
print(f"\n  Transação criada (ainda SEM assinatura): {tx}")

tx.sign_transaction(alice)
print(f"  Transação assinada com a chave privada da Alice.")
print(f"  Assinatura (hex, resumida): {tx.signature[:32]}...")

tx.save("transacao.json")
print("\n  (Transação assinada salva em transacao.json.)")

print(
    "\n  A assinatura é gerada a partir do CONTEÚDO da transação (remetente,\n"
    "  destinatário e valor) usando a chave privada da Alice. Só quem tem\n"
    "  essa chave privada consegue gerar uma assinatura que combine com o\n"
    "  endereço da Alice — é assim que a rede sabe que foi ela quem\n"
    "  autorizou o envio."
)
