"""
tamper_attack.py
------------------------
Leia a explicação deste passo no README.md.

Execute com:
    python3 tamper_attack.py

Pré-requisito: rode antes o build_chain.py (ele cria o arquivo
cadeia.json que este script carrega). Este script salva o resultado em
cadeia_adulterada.json + ataque_info.json, para o próximo passo
(tamper_fix_attempt.py) continuar.

Comando extra deste mesmo passo: depois de rodar este script, rode
também check_validity.py — ele só faz a verificação, sem atacar
nada, para você ver essa operação isolada.
"""

import json
import os
import sys

from blockchain import Blockchain
from lab_utils import ask, pause, title

if not os.path.exists("cadeia.json"):
    sys.exit(
        "Arquivo cadeia.json não encontrado.\n"
        "Rode primeiro: python3 build_chain.py"
    )

title("Onde mora a segurança? Tente atacar a cadeia você mesmo")

bc = Blockchain.load("cadeia.json")
print(f"  Cadeia carregada de cadeia.json ({len(bc.chain)} blocos).")

max_index = bc.last_block.index
if max_index < 2:
    sys.exit(
        "Esta cadeia só tem 1 bloco além do gênesis, e o último bloco não\n"
        "pode ser escolhido para o ataque (veja o motivo no README.md).\n"
        "Rode novamente o build_chain.py e crie pelo menos 2 blocos."
    )

# O ÚLTIMO bloco fica de fora de propósito: se ele fosse adulterado, não
# haveria um bloco seguinte para acusar o previous_hash desatualizado, e a
# cadeia pareceria válida de novo — o que esconderia a lição deste passo.
limite = max_index - 1
idx_str = ask(f"Qual bloco você quer adulterar? (1 a {limite})", "1")
try:
    idx = max(1, min(limite, int(idx_str)))
except ValueError:
    idx = 1

conteudo_original = bc.chain[idx].transactions
print(f"\n  Conteúdo original do bloco {idx}: {conteudo_original}")

novo_conteudo = ask("Digite o novo conteúdo 'fraudulento'", "Apagar minha dívida de 1000 moedas")
bc.tamper_block(idx, [novo_conteudo])

print(f"\n  Conteúdo alterado do bloco {idx}: {bc.chain[idx].transactions}")

bc.save("cadeia_adulterada.json")
with open("ataque_info.json", "w", encoding="utf-8") as f:
    json.dump({"indice_atacado": idx}, f)
print("\n  (Estado salvo em cadeia_adulterada.json)")
