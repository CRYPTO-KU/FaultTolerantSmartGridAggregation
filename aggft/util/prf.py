import pyaes

################################################################################
# PRF Utility Functions
################################################################################

# Use AES with CTR mode as a PRF
def PRF(key: bytes, input: int) -> int:
    aes = pyaes.AESModeOfOperationCTR(key)
    ctx = aes.encrypt(f"{input}")
    return int.from_bytes(ctx, byteorder = "little")
