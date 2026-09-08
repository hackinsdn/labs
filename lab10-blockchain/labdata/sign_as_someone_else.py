"""
sign_as_someone_else.py
---------------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 sign_as_someone_else.py

Pré-requisito: rode antes o create_wallet.py (ele cria os
arquivos carteira_alice.json e carteira_bob.json que este script
carrega).
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

title("(bônus) Tentando assinar em nome de outra pessoa")

alice = Wallet.load("carteira_alice.json")
bob = Wallet.load("carteira_bob.json")

valor_str = ask("Quantas moedas o 'Bob' vai tentar roubar da Alice?", "999")
try:
    valor = float(valor_str)
except ValueError:
    valor = 999

print(
    f"\n  O Bob monta uma transação que diz: 'Alice envia {valor} moedas para o Bob'\n"
    "  (ou seja, sender = endereço da Alice), mas ele só tem a PRÓPRIA\n"
    "  chave privada — não a da Alice."
)

tx = Transaction(sender_address=alice.address, recipient_address=bob.address, amount=valor)

try:
    tx.sign_transaction(bob,force="--force" in sys.argv)
    print("\n  A transação foi assinada?! Sim! Isso não deveria acontecer.")
    tx.save("transacao_adulterada.json")
    print("\n  Transação adulterada salva em transacao_adulterada.json")
except ValueError as e:
    print(f"\n  Erro ao tentar assinar: {e}")

print(
    "\n  O código de Transaction.sign_transaction() verifica explicitamente\n"
    "  se `wallet.address == self.sender` antes de assinar. Mesmo sem essa\n"
    "  checagem explícita, se o Bob 'forçasse' uma assinatura com a própria\n"
    "  chave, ela simplesmente não bateria na verificação com a chave\n"
    "  pública da Alice (o mesmo is_signature_valid() de verify_signature.py) — então,\n"
    "  de um jeito ou de outro, o ataque não passa."
)
print("\nFim da Atividade 3 — e do lab! Volte ao README.md para os exercícios propostos.")
