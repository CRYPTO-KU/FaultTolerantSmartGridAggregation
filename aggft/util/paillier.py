from typing import Tuple

from phe.paillier import EncryptedNumber, PaillierPublicKey


################################################################################
# Helper Functions
################################################################################


def serialize_encrypted_number(m: EncryptedNumber) -> Tuple[str, str]:
    return (str(m.ciphertext()), str(m.exponent))


def deserialize_encrypted_number(
    m: Tuple[str, str], pk: PaillierPublicKey
) -> EncryptedNumber:
    return EncryptedNumber(pk, int(m[0]), int(m[1]))
