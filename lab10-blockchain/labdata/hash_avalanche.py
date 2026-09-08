"""
hash_avalanche.py
-------------------------
Leia a explicação deste passo no README.md antes ou
depois de rodar — o texto completo do conceito está lá, aqui é só o
código que você vai executar.

Execute com:
    python3 hash_avalanche.py
"""

import hashlib

from lab_utils import ask, title

title("O efeito avalanche do hash SHA-256")

texto1 = ask("Digite uma frase qualquer", "Enviar 10 moedas para Bob")
hash1 = hashlib.sha256(texto1.encode()).hexdigest()
print(f"\n  Texto:  {texto1!r}")
print(f"  Hash:   {hash1}")

default2 = texto1.replace("10", "11") if "10" in texto1 else texto1 + "!"
print("\n>>> Agora mude só UM detalhe da frase (ex.: 10 -> 11) e veja o novo hash...")
texto2 = ask("Digite a frase modificada", default2)
hash2 = hashlib.sha256(texto2.encode()).hexdigest()
print(f"\n  Texto:  {texto2!r}")
print(f"  Hash:   {hash2}")

diffs = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
print(f"\n  Caracteres diferentes entre os dois hashes: {diffs} de {len(hash1)}")
