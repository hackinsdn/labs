"""
blockchain.py
-------------
Define a estrutura que encadeia os blocos (Block, ver block.py) e as
regras que tornam a cadeia "confiável": cada bloco referencia o hash
do bloco anterior, e a validade da cadeia inteira pode ser checada a
qualquer momento recalculando os hashes.

Conceito-chave: não existe um "banco de dados central" guardando o
estado. A confiança vem da matemática (hashes encadeados) e do
consenso (Proof of Work), não de uma autoridade central.
"""

import json

from block import Block


class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain = [self._create_genesis_block()]

    def _create_genesis_block(self):
        """O primeiro bloco da cadeia (não tem bloco anterior de verdade)."""
        return Block(index=0, transactions=["Genesis Block"], previous_hash="0")

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        """
        Cria um novo bloco, minera (Proof of Work) e o adiciona à cadeia.
        Retorna o bloco criado e as estatísticas de mineração.
        """
        new_block = Block(
            index=self.last_block.index + 1,
            transactions=transactions,
            previous_hash=self.last_block.hash,
        )
        stats = new_block.mine(self.difficulty)
        self.chain.append(new_block)
        return new_block, stats

    def is_chain_valid(self):
        """
        Verifica a integridade de toda a cadeia:
          1. O hash armazenado de cada bloco bate com o hash recalculado
             a partir do conteúdo atual do bloco (detecta adulteração de dados).
          2. O previous_hash de cada bloco bate com o hash real do bloco
             anterior (detecta blocos "arrancados"/reordenados/substituídos).
          3. (bônus) O hash de cada bloco (exceto o gênesis) respeita a
             dificuldade de mineração configurada.

        Retorna (bool, lista_de_problemas_encontrados).
        """
        problems = []

        for i in range(len(self.chain)):
            current = self.chain[i]

            if current.hash != current.compute_hash():
                problems.append(
                    f"Bloco {current.index}: hash armazenado não bate com o "
                    f"hash recalculado (dados foram adulterados!)."
                )

            if i > 0:
                previous = self.chain[i - 1]
                if current.previous_hash != previous.hash:
                    problems.append(
                        f"Bloco {current.index}: previous_hash não corresponde "
                        f"ao hash real do bloco {previous.index} (cadeia quebrada!)."
                    )

        return (len(problems) == 0, problems)

    def tamper_block(self, index, new_transactions):
        """
        Função DIDÁTICA para simular um ataque: altera os dados de um
        bloco já existente SEM re-minerar, deixando o hash "hash" antigo
        (inconsistente com o novo conteúdo). Use isso para demonstrar
        que is_chain_valid() detecta a fraude.
        """
        if index < 0 or index >= len(self.chain):
            raise IndexError("Índice de bloco inválido.")
        self.chain[index].transactions = new_transactions
        # Note: propositalmente NÃO recalculamos/re-mineramos o hash aqui,
        # para simular um atacante que tenta editar dados "por baixo dos panos".

    def __repr__(self):
        return f"Blockchain(blocks={len(self.chain)}, difficulty={self.difficulty})"

    def to_dict(self):
        return {
            "difficulty": self.difficulty,
            "chain": [b.to_dict() for b in self.chain],
        }

    def save(self, path):
        """
        Salva a cadeia inteira em um arquivo JSON. Usado neste lab para
        passar o estado de um script (step) para o próximo, já que cada
        passo do lab agora é um programa Python independente.
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False, default=str)

    @classmethod
    def load(cls, path):
        """Carrega uma cadeia previamente salva com save(), sem recalcular nada."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        bc = cls.__new__(cls)
        bc.difficulty = data["difficulty"]
        bc.chain = [Block.from_dict(bd) for bd in data["chain"]]
        return bc
