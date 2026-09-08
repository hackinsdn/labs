"""
create_wallet.py
-------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 create_wallet.py

Cria duas carteiras (Alice e Bob) e salva em carteira_alice.json e
carteira_bob.json, para os próximos passos continuarem de onde você
parou.
"""

from wallet import Wallet
from lab_utils import title

title("Criando carteiras (pares de chaves)")

alice = Wallet()
bob = Wallet()

print("  Carteira da Alice criada.")
print(f"    Endereço (chave pública, hex):  {alice.address}")
print(f"    Chave privada (hex, resumida):  {alice.private_key.to_string().hex()[:20]}... (SECRETA!)")

print("\n  Carteira do Bob criada.")
print(f"    Endereço (chave pública, hex):  {bob.address}")
print(f"    Chave privada (hex, resumida):  {bob.private_key.to_string().hex()[:20]}... (SECRETA!)")

alice.save("carteira_alice.json")
bob.save("carteira_bob.json")
print("\nCarteiras salvas em carteira_alice.json e carteira_bob.json")
