import secrets

from typing import Tuple

import pyaes

from phe.paillier import (
    generate_paillier_keypair,
    PaillierPrivateKey,
    PaillierPublicKey,
    EncryptedNumber,
)

################################################################################
# PRF Types
################################################################################

PRFKey = bytes

################################################################################
# PRF Functions
################################################################################


def generate_prf_key(length: int) -> PRFKey:
    return secrets.token_bytes(length)


# Use AES with CTR mode as a PRF
def prf(key: PRFKey, input: int) -> int:
    aes = pyaes.AESModeOfOperationCTR(key)
    ctx = aes.encrypt(f"{input}")
    return int.from_bytes(ctx, byteorder="little")


################################################################################
# Homomorphic Encryption Types
################################################################################

HomomorphicPrivateKey = PaillierPrivateKey
HomomorphicPublicKey = PaillierPublicKey
HomomorphicNumber = EncryptedNumber

################################################################################
# Homomorphic Encryption Functions
################################################################################


def generate_homomorphic_keypair(
    length: int,
) -> Tuple[HomomorphicPrivateKey, HomomorphicPublicKey]:
    pk, sk = generate_paillier_keypair(n_length=length)
    return sk, pk


def serialize_homomorphic_number(m: HomomorphicNumber) -> Tuple[str, str]:
    return (str(m.ciphertext()), str(m.exponent))


def deserialize_homomorphic_number(
    m: Tuple[str, str], pk: HomomorphicPublicKey
) -> HomomorphicNumber:
    return HomomorphicNumber(pk, int(m[0]), int(m[1]))
