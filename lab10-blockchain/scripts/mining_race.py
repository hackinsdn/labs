"""
mining_race.py
-----------------------

Execute com:
    python3 mining_race.py
"""

from block import Block
from lab_utils import ask, title

title("Simulando uma corrida entre dois mineradores")

dificuldade_str = ask("Escolha uma dificuldade para a corrida (recomendado: 3 a 5)", "4")
try:
    dificuldade = max(1, min(6, int(dificuldade_str)))
except ValueError:
    dificuldade = 4

print(
    "\n  Dois mineradores competem para minerar o MESMO bloco pendente.\n"
    "  Na vida real, cada minerador inclui seu próprio endereço na\n"
    "  transação de recompensa — então, mesmo minerando o 'mesmo' bloco,\n"
    "  o conteúdo de cada um é ligeiramente diferente, e cada um percorre\n"
    "  uma sequência diferente de hashes."
)

transacoes_base = ["Alice paga 5 moedas para Bob"]

bloco_a = Block(
    index=1,
    transactions=transacoes_base + ["Recompensa de mineração: Minerador A"],
    previous_hash="0" * 64,
)
bloco_b = Block(
    index=1,
    transactions=transacoes_base + ["Recompensa de mineração: Minerador B"],
    previous_hash="0" * 64,
)

stats_a = bloco_a.mine(dificuldade)
stats_b = bloco_b.mine(dificuldade)

print(f"\n  Minerador A: nonce={bloco_a.nonce}, tentativas={stats_a['attempts']}, tempo={stats_a['elapsed_seconds']:.4f}s")
print(f"  Minerador B: nonce={bloco_b.nonce}, tentativas={stats_b['attempts']}, tempo={stats_b['elapsed_seconds']:.4f}s")

if stats_a["attempts"] < stats_b["attempts"]:
    vencedor = "Minerador A"
elif stats_b["attempts"] < stats_a["attempts"]:
    vencedor = "Minerador B"
else:
    vencedor = "Empate! (raro)"

print(f"\n  Quem encontrou um nonce válido primeiro: {vencedor}")

print(
    "\n  Isso é essencialmente a 'loteria' do Proof of Work: como o hash se\n"
    "  comporta de forma imprevisível, não dá para saber de antemão quem vai\n"
    "  encontrar o nonce vencedor primeiro — só quem tem mais poder\n"
    "  computacional tem mais CHANCES estatísticas, rodada após rodada. É\n"
    "  assim que a rede decide, de forma descentralizada, quem propaga o\n"
    "  próximo bloco."
)
