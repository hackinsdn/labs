"""
block.py
--------
Define a estrutura fundamental de um blockchain: o Bloco.

Cada bloco guarda:
  - index: posição do bloco na cadeia
  - timestamp: quando o bloco foi criado
  - transactions: lista de transações (ou qualquer dado) armazenadas no bloco
  - previous_hash: hash do bloco anterior (é isso que "encadeia" os blocos)
  - nonce: número usado uma única vez, ajustado durante a mineração (Proof of Work)
  - hash: hash SHA-256 calculado a partir de todos os campos acima

Conceito-chave: se QUALQUER campo do bloco mudar (mesmo 1 caractere),
o hash resultante muda completamente. É isso que torna o blockchain
resistente a adulteração (tamper-evident).
"""

import hashlib
import json
import time


class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        # O hash é calculado por último, pois depende de todos os outros campos
        self.hash = self.compute_hash()

    def compute_hash(self):
        """
        Serializa o conteúdo do bloco em JSON (de forma determinística,
        com sort_keys=True) e calcula o SHA-256 sobre essa string.
        """
        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        block_string = json.dumps(block_content, separators=(",", ":"), sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        """
        Proof of Work (PoW): incrementa o nonce até que o hash do bloco
        comece com `difficulty` zeros à esquerda.

        Isso simula o "trabalho computacional" que protege redes como o
        Bitcoin: encontrar esse hash exige tentativa e erro (força bruta),
        mas qualquer pessoa pode VERIFICAR o resultado instantaneamente.
        """
        target = "0" * difficulty
        attempts = 0
        start = time.time()

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
            attempts += 1

        elapsed = time.time() - start
        return {"attempts": attempts, "elapsed_seconds": elapsed}

    def __repr__(self):
        return (
            f"Block(index={self.index}, nonce={self.nonce}, "
            f"hash={self.hash[:16]}..., previous_hash={self.previous_hash[:16]}...)"
        )

    def to_dict(self):
        """Representação do bloco pronta para salvar em JSON (inclui o hash)."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Reconstrói um Block a partir de um dicionário salvo anteriormente
        (por exemplo, carregado de um arquivo JSON entre um script e outro).

        Importante: o hash é restaurado EXATAMENTE como estava salvo, sem
        recalcular — isso é o que permite carregar até uma cadeia que foi
        deliberadamente adulterada (para os exercícios de tampering) e
        continuar exatamente de onde ela parou.
        """
        block = cls.__new__(cls)
        block.index = data["index"]
        block.timestamp = data["timestamp"]
        block.transactions = data["transactions"]
        block.previous_hash = data["previous_hash"]
        block.nonce = data["nonce"]
        block.hash = data["hash"]
        return block
