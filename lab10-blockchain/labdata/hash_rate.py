"""
hash_rate.py
---------------------

Execute com:
    python3 hash_rate.py

Este script NÃO minera de verdade nas dificuldades altas — ele mede a
velocidade de hashing da sua máquina e ESTIMA quanto tempo levaria.
"""

import hashlib
import time

from lab_utils import ask, title

title("Medindo o hash rate da sua máquina e estimando o custo futuro")

print("  Calibrando por meio segundo (calculando SHA-256 repetidamente)...")

fim = time.time() + 0.5
contagem = 0
texto = b"calibracao de hash rate"
while time.time() < fim:
    hashlib.sha256(texto + str(contagem).encode()).hexdigest()
    contagem += 1

hash_rate = contagem / 0.5
print(f"  Hash rate estimado desta máquina: {hash_rate:,.0f} hashes/segundo".replace(",", "."))

dificuldades_str = ask("Para quais dificuldades você quer estimar o tempo? (separadas por vírgula)", "6,7,8")
try:
    dificuldades = [int(d.strip()) for d in dificuldades_str.split(",") if d.strip()]
except ValueError:
    dificuldades = [6, 7, 8]

print("\n  Estimativas (tentativas esperadas = 16^dificuldade):\n")
for d in dificuldades:
    tentativas_esperadas = 16 ** d
    segundos = tentativas_esperadas / hash_rate
    if segundos < 60:
        tempo_str = f"{segundos:.1f} segundos"
    elif segundos < 3600:
        tempo_str = f"{segundos / 60:.1f} minutos"
    elif segundos < 86400:
        tempo_str = f"{segundos / 3600:.1f} horas"
    else:
        tempo_str = f"{segundos / 86400:.1f} dias"
    print(f"    dificuldade={d}: ~{tentativas_esperadas:,} tentativas esperadas -> ~{tempo_str}".replace(",", "."))

print(
    "\n  Isso é só a sua CPU rodando um núcleo, em Python (lento comparado a\n"
    "  hardware dedicado). Mineradores de Bitcoin reais usam chips ASIC que\n"
    "  calculam bilhões de hashes por segundo — e mesmo assim a rede ajusta\n"
    "  a dificuldade global para que um bloco novo demore ~10 minutos. Isso\n"
    "  te dá uma ideia de por que reescrever o histórico é inviável na prática."
)

