"""
wallet.py
---------
Demonstra o uso de criptografia de chave pública (ECDSA) para simular
"carteiras" (wallets) capazes de assinar e verificar transações — o
mesmo princípio usado pelo Bitcoin e pela Ethereum.

Conceitos-chave:
  - Chave privada: em segredo, é usada para ASSINAR transações. Provar
    que "eu" autorizei essa transação, sem revelar a chave privada.
  - Chave pública: pode ser compartilhada livremente (é praticamente o
    seu "endereço"/identidade na rede). É usada para VERIFICAR se uma
    assinatura foi de fato gerada pela chave privada correspondente.
  - Uma transação assinada não pode ser forjada por outra pessoa, e
    qualquer alteração no conteúdo da transação invalida a assinatura.
"""

import json
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError


class Wallet:
    def __init__(self):
        # SECP256k1 é a mesma curva elíptica usada pelo Bitcoin/Ethereum
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    @property
    def address(self):
        """Endereço público simplificado: hex da chave pública."""
        return self.public_key.to_string().hex()

    def sign(self, message: str) -> str:
        """Assina uma mensagem (string) com a chave privada. Retorna hex."""
        signature = self.private_key.sign(message.encode())
        return signature.hex()

    def save(self, path):
        """
        Salva a chave privada em um arquivo JSON, para que outro script do
        lab possa carregar a MESMA carteira depois (só para fins didáticos —
        numa aplicação real, a chave privada nunca deveria ser salva assim,
        em texto simples, sem proteção).
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"private_key_hex": self.private_key.to_string().hex()}, f)

    @classmethod
    def load(cls, path):
        """Recarrega uma carteira salva com save(), reconstruindo as duas chaves."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        wallet = cls.__new__(cls)
        wallet.private_key = SigningKey.from_string(
            bytes.fromhex(data["private_key_hex"]), curve=SECP256k1
        )
        wallet.public_key = wallet.private_key.get_verifying_key()
        return wallet


class Transaction:
    def __init__(self, sender_address, recipient_address, amount):
        self.sender = sender_address
        self.recipient = recipient_address
        self.amount = amount
        self.signature = None

    def to_dict(self, include_signature=False):
        data = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
        }
        if include_signature:
            data["signature"] = self.signature
        return data

    def _message(self):
        """Representação determinística da transação para assinar/verificar."""
        return json.dumps(self.to_dict(include_signature=False), sort_keys=True)

    def sign_transaction(self, wallet: Wallet, force=False):
        """
        A carteira do REMETENTE assina a transação. Isso prova que quem
        está gastando o valor é o dono da chave privada correspondente
        ao endereço `sender`.
        """
        if wallet.address != self.sender and not force:
            raise ValueError("Só o dono da chave privada do remetente pode assinar.")
        self.signature = wallet.sign(self._message())

    def is_signature_valid(self) -> bool:
        """
        Verifica a assinatura usando a CHAVE PÚBLICA do remetente
        (recuperada a partir do endereço `sender`), sem precisar da
        chave privada em nenhum momento.
        """
        if self.signature is None:
            return False
        try:
            sender_public_key = VerifyingKey.from_string(
                bytes.fromhex(self.sender), curve=SECP256k1
            )
            sender_public_key.verify(
                bytes.fromhex(self.signature), self._message().encode()
            )
            return True
        except (BadSignatureError, ValueError):
            return False

    def __repr__(self):
        short_sender = self.sender[:10] + "..." if self.sender else "COINBASE"
        short_recipient = self.recipient[:10] + "..."
        return f"Transaction({short_sender} -> {short_recipient}: {self.amount})"

    def save(self, path):
        """Salva a transação (com a assinatura, se houver) em um arquivo JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(include_signature=True), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        """Recarrega uma transação salva com save(), incluindo a assinatura."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        tx = cls(sender_address=data["sender"], recipient_address=data["recipient"], amount=data["amount"])
        tx.signature = data.get("signature")
        return tx
