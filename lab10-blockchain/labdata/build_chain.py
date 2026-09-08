"""
build_chain.py
----------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 build_chain.py

Este script salva a cadeia criada em cadeia.json, para que o
próximo passo (tamper_attack.py) continue de onde você parou.
"""

from blockchain import Blockchain
from lab_utils import ask, pause, title

title("Encadeando blocos: onde a 'corrente' realmente mora")

bc = Blockchain(difficulty=2)  # dificuldade baixa aqui só para o exemplo ser rápido
print("  Bloco gênesis criado (o primeiro, sem antecessor real):")
print(f"    hash={bc.last_block.hash[:24]}...")

n_blocos_str = ask("Quantos blocos você quer adicionar à cadeia?", "4")
try:
    n_blocos = max(1, min(6, int(n_blocos_str)))
except ValueError:
    n_blocos = 4

for i in range(1, n_blocos + 1):
    transacao = ask(f"  Transação para o bloco {i}", f"Transação de exemplo #{i}")
    hash_anterior = bc.last_block.hash
    block, stats = bc.add_block([transacao])
    print(f"\n  Bloco {i} minerado (nonce={block.nonce}, {stats['attempts']} tentativas):")
    print(f"    previous_hash = {block.previous_hash[:24]}...")
    print(f"    hash          = {block.hash[:24]}...")
    igual = block.previous_hash == hash_anterior
    print(f"    previous_hash bate com o hash do bloco anterior? {igual}  <-- é isso que forma o elo")
    pause()

print("\n  Visualização da cadeia (hashes truncados):\n")
for b in bc.chain:
    print(f"    [Bloco {b.index}] prev={b.previous_hash[:10]}... -> hash={b.hash[:10]}...")
    if b.index < bc.chain[-1].index:
        print("         |")
        print("         v")

valido, _ = bc.is_chain_valid()
print(f"\n  is_chain_valid() -> {valido}")

bc.save("cadeia.json")
print("\nCadeia salva em cadeia.json")
