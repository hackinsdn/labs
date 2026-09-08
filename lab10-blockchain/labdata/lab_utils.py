"""
lab_utils.py
------------
Pequenas funções de apoio usadas pelos scripts deste lab (entrada
interativa, pausas, separadores visuais).

Isso não é conteúdo do lab em si — é só o "encanamento" para os scripts
de cada passo ficarem curtos e fáceis de ler.
"""

import sys
import time

# Se não houver um terminal interativo de verdade (ex: rodando em
# automação/testes), os scripts seguem sozinhos usando valores padrão,
# em vez de travar esperando um ENTER que nunca vai chegar.
AUTO_MODE = not sys.stdin.isatty()


def pause(msg="\n>>> Pressione ENTER para continuar..."):
    if AUTO_MODE:
        print(msg + " [modo automático: continuando sozinho]")
        time.sleep(0.2)
        return
    input(msg)


def ask(prompt, default):
    if AUTO_MODE:
        print(f"{prompt} [modo automático, usando padrão: {default!r}]")
        return default
    resposta = input(f"{prompt} (ENTER para usar '{default}'): ").strip()
    return resposta if resposta else default


def title(t):
    print("\n" + "=" * 70)
    print(t)
    print("=" * 70)
