"""
tamper_transaction.py
-------------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 tamper_transaction.py

Pré-requisito: rode antes o sign_transaction.py (ele cria o
arquivo transacao.json que este script carrega e adultera).
"""

import os
import sys

from wallet import Transaction
from lab_utils import ask, pause, title

if not os.path.exists("transacao.json"):
    sys.exit(
        "Arquivo transacao.json não encontrado.\n"
        "Rode primeiro: python3 sign_transaction.py"
    )

title("Tentando fraudar uma transação já assinada")

tx = Transaction.load("transacao.json")
print(f"  Transação original (assinada): {tx}")
print(f"  Assinatura ainda válida? {tx.is_signature_valid()}")

novo_valor_str = ask("\nDigite um novo valor 'fraudulento' para a transação", str(tx.amount * 100))
try:
    novo_valor = float(novo_valor_str)
except ValueError:
    novo_valor = tx.amount * 100

tx.amount = novo_valor
print(f"\n  Transação adulterada (valor mudou, assinatura NÃO foi refeita): {tx}")

pause("\n>>> Pressione ENTER para verificar a assinatura de novo...")

valida = tx.is_signature_valid()
print(f"\n  is_signature_valid() -> {valida}")

print(
    "\n  A assinatura foi calculada sobre o conteúdo ORIGINAL da transação.\n"
    "  Mudar o valor muda a mensagem que é comparada com a assinatura na\n"
    "  hora de verificar — e a verificação falha. Isso é o mesmo efeito\n"
    "  avalanche da Atividade 1, aplicado agora a assinaturas digitais: não dá\n"
    "  para 'ajustar' uma transação assinada sem invalidar a assinatura."
)
