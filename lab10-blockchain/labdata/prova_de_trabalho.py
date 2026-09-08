#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
  Prova de Trabalho (Proof of Work) — demonstração visual
  Prof. Ana Carolina Sokolonski — IFBA, Campus Feira de Santana
============================================================================

Ilustra, de forma simples e VISUAL, a ideia central da mineração por
Prova de Trabalho usada em blockchains como o Bitcoin:

    variar um número (o "nonce") e recalcular o hash SHA-256 do bloco
    até que o hash comece com uma quantidade exigida de zeros.

Essa quantidade de zeros é a "dificuldade". Achar o nonce é difícil
(força bruta); conferir se ele está correto é trivial (um só hash).

Não usa nenhuma biblioteca externa — apenas a biblioteca padrão.

    Execute:   python prova_de_trabalho.py

Dica de sala: rode com dificuldades maiores para ver o tempo explodir:
    python prova_de_trabalho.py 6

Observação (Compilaí): a dificuldade padrão é 5, igual ao terminal. É a
parte "cara de propósito" da demonstração — no compilador online a
mineração deste bloco leva uns 15–20s (o SHA-256 aí é reimplementado em
Python puro dentro de um interpretador de Python no navegador, então cada
hash custa bem mais que num Python real). Vale a pena esperar uma vez para
ver o relógio andando: é exatamente o ponto que a demo quer passar.
============================================================================
"""

import hashlib
import time
import sys
import os

# Em Windows 10+ este comando "acorda" o suporte a cores ANSI no terminal.
if os.name == "nt":
    os.system("")


# ---------------------------------------------------------------------------
#  Cores ANSI — deixam a saída bem visual
# ---------------------------------------------------------------------------
class Cor:
    RESET = "\033[0m"
    NEG   = "\033[1m"   # negrito
    FRACO = "\033[2m"   # esmaecido
    VERDE = "\033[92m"
    VERM  = "\033[91m"
    AMAR  = "\033[93m"
    AZUL  = "\033[96m"
    CINZA = "\033[90m"


# Só usamos cor se a saída for um terminal de verdade (ou se forçado).
USAR_COR = sys.stdout.isatty() or os.environ.get("FORCE_COLOR") == "1"


def c(texto, *codigos):
    """Envolve o texto com códigos de cor (ou devolve puro, sem terminal)."""
    if not USAR_COR:
        return texto
    return "".join(codigos) + texto + Cor.RESET


# ---------------------------------------------------------------------------
#  Núcleo da Prova de Trabalho
# ---------------------------------------------------------------------------
def calcular_hash(indice, dados, hash_anterior, nonce):
    """
    Monta o conteúdo do bloco e devolve seu hash SHA-256 (hexadecimal).
    Repare que o 'hash_anterior' entra no cálculo — é ele que ENCADEIA
    os blocos, formando a "corrente" da blockchain.
    """
    conteudo = f"{indice}|{dados}|{hash_anterior}|{nonce}"
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def contar_zeros_iniciais(hash_hex):
    """Quantos caracteres '0' aparecem no início do hash (proxy visual de
    'quão perto' uma tentativa chegou do alvo)."""
    n = 0
    for ch in hash_hex:
        if ch != "0":
            break
        n += 1
    return n


def destacar(hash_hex, dificuldade, ok):
    """Pinta de verde os zeros iniciais quando o hash é válido."""
    prefixo, resto = hash_hex[:dificuldade], hash_hex[dificuldade:]
    if ok:
        return c(prefixo, Cor.VERDE, Cor.NEG) + c(resto, Cor.CINZA)
    return c(hash_hex[:dificuldade + 8] + "…", Cor.CINZA)


def minerar_e_amostrar(indice, dados, hash_anterior, dificuldade,
                        mostrar_ao_vivo=True, passo=20000, max_amostras=6):
    """
    Igual a minerar(), mas também guarda ALGUMAS tentativas ao longo do
    caminho (nonce, hash) — sem custo extra relevante, é só anotar valores
    que já foram calculados. Serve para depois desenhar uma tabela
    mostrando visualmente que quase toda tentativa erra feio, até uma só
    acertar todos os zeros exigidos.
    """
    alvo = "0" * dificuldade
    inicio = time.time()
    nonce = 0
    amostras = []          # cada item: (nonce, hash, venceu?)
    passo_amostra = 1
    proxima_amostra = 0

    while True:
        h = calcular_hash(indice, dados, hash_anterior, nonce)

        if h.startswith(alvo):
            duracao = time.time() - inicio
            amostras.append((nonce, h, True))
            if mostrar_ao_vivo and USAR_COR:
                print("\r" + " " * 78, end="\r")
            return nonce, h, nonce + 1, duracao, amostras

        # Amostra em espaçamento crescente (0, 1, 5, 21, 85, ...) — assim,
        # mesmo quando o nonce vencedor é grande, sobra amostra espalhada
        # do começo ao fim da busca.
        if nonce == proxima_amostra and len(amostras) < max_amostras:
            amostras.append((nonce, h, False))
            passo_amostra *= 4
            proxima_amostra = nonce + passo_amostra

        if mostrar_ao_vivo and USAR_COR and nonce % passo == 0:
            print("\r  " + c("⛏  minerando", Cor.AMAR)
                  + f"  nonce = {c(f'{nonce:>12,}', Cor.NEG)}"
                  + f"   hash = {c(h[:20] + '…', Cor.CINZA)}",
                  end="", flush=True)
        nonce += 1


# ---------------------------------------------------------------------------
#  Apresentação
# ---------------------------------------------------------------------------
def titulo(txt):
    linha = "═" * 74
    print("\n" + c(linha, Cor.AZUL))
    print(c("  " + txt, Cor.AZUL, Cor.NEG))
    print(c(linha, Cor.AZUL))


def mostrar_bloco(indice, dados, hash_anterior, dificuldade,
                  nonce, h, tentativas, duracao):
    taxa = tentativas / duracao if duracao > 0 else 0
    print("  " + c("✔ BLOCO MINERADO", Cor.VERDE, Cor.NEG))
    print(f"     índice ........ {indice}")
    print(f"     dados ......... {c(dados, Cor.AZUL)}")
    print(f"     hash anterior . {c(hash_anterior[:28] + '…', Cor.CINZA)}")
    print(f"     dificuldade ... {c(str(dificuldade) + ' zeros', Cor.AMAR)}"
          f"  (alvo: {c('0'*dificuldade + '…', Cor.VERDE)})")
    print(f"     nonce ......... {c(f'{nonce:,}', Cor.NEG)}"
          f"   {c('← o número que resolve o quebra-cabeça', Cor.FRACO)}")
    print(f"     hash .......... {destacar(h, dificuldade, ok=True)}")
    print(f"     tentativas .... {tentativas:,}")
    print(f"     tempo ......... {duracao:.3f}s   "
          f"({taxa:,.0f} hashes/s)")


def tabela_amostras(amostras):
    """Mostra, em forma de tabelinha com barrinhas, algumas tentativas reais
    ao longo do caminho: a esmagadora maioria erra (poucos ou nenhum zero
    inicial) até a última acertar todos os zeros exigidos."""
    print()
    print("  " + c("tentativas ao longo do caminho (amostra):", Cor.NEG))
    print(f"  {'nonce':>12}   {'hash (prefixo)':<16}  zeros à esquerda")
    print("  " + c("─" * 62, Cor.CINZA))
    for nonce, h, venceu in amostras:
        zeros = contar_zeros_iniciais(h)
        cor_barra = Cor.VERDE if venceu else Cor.AMAR
        marca = c("  ← GANHOU!", Cor.VERDE, Cor.NEG) if venceu else ""
        print(f"  {nonce:>12,}   {h[:16]}  "
              + c("█" * zeros, cor_barra) + c("░" * (8 - min(zeros, 8)), Cor.CINZA)
              + f"  ({zeros})" + marca)
    print("  " + c("→ Cada tentativa é essencialmente um sorteio novo: nada garante que"
                    " o zero seguinte 'já vem'.", Cor.FRACO))


def demo_mineracao(dificuldade):
    """Minera um bloco ao vivo e ilustra o caminho até achar o nonce."""
    titulo("1. MINERANDO UM BLOCO AO VIVO")
    indice        = 1
    dados         = "Ana paga 10 BTC para Bruno"
    hash_anterior = "0" * 64          # bloco génesis não tem anterior

    print(f"  Objetivo: achar um nonce cujo hash comece com "
          f"{c(str(dificuldade) + ' zeros', Cor.AMAR)}.\n")

    nonce, h, tentativas, dur, amostras = minerar_e_amostrar(
        indice, dados, hash_anterior, dificuldade)
    mostrar_bloco(indice, dados, hash_anterior, dificuldade,
                  nonce, h, tentativas, dur)
    tabela_amostras(amostras)
    return indice, dados, hash_anterior, dificuldade, nonce, h


def main():
    # Dificuldade pela linha de comando (padrão 5). Ex.: python ... 6
    try:
        dificuldade = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    except ValueError:
        dificuldade = 5
    dificuldade = max(1, min(dificuldade, 7))   # limites de segurança

    print(c("\n  PROVA DE TRABALHO — como um bloco é 'minerado'", Cor.NEG))
    if not USAR_COR:
        print("  (dica: rode num terminal para ver as cores e a animação)")

    demo_mineracao(dificuldade)

    print(c("\n  Fim. Experimente aumentar a dificuldade: "
            "python prova_de_trabalho.py 6\n", Cor.FRACO))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\n  Interrompido pelo usuário.\n", Cor.AMAR))
