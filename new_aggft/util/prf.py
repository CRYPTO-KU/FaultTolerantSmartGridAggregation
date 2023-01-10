import pyaes

################################################################################
# PRF Utility Functions
################################################################################

# Use AES with CTR mode as a PRF
def PRF(key: bytes, input: int) -> int:
    aes = pyaes.AESModeOfOperationCTR(key)
    bytes = aes.encrypt(f"{input}")
    return int.from_bytes(bytes, byteorder = "little")
