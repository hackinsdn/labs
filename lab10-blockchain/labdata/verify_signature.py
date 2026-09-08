"""
verify_signature.py
----------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 verify_signature.py

Pré-requisito: rode antes o sign_transaction.py (ele cria o
arquivo transacao.json que este script carrega).
"""

import os
import sys

from wallet import Transaction
from lab_utils import title

arquivo = "transacao.json"
if len(sys.argv) > 1:
    arquivo = sys.argv[1]
if not os.path.exists(arquivo):
    sys.exit(
        "Arquivo transacao.json não encontrado.\n"
        "Rode primeiro: python3 sign_transaction.py"
    )

title("Verificando a assinatura com a chave pública")

tx = Transaction.load(arquivo)
print(f"  Transação carregada: {tx}")
print(f"  Assinatura (hex, resumida): {tx.signature[:32]}...")

valida = tx.is_signature_valid()
print(f"\n  is_signature_valid() -> {valida}")

print(
    "\n  Repare que a verificação usa só o endereço (chave PÚBLICA) da\n"
    "  Alice, recuperado do próprio campo 'sender' da transação — em\n"
    "  nenhum momento a chave privada dela é necessária para conferir a\n"
    "  assinatura. Isso é o que torna a verificação possível para\n"
    "  QUALQUER pessoa na rede, sem precisar confiar em ninguém."
)
