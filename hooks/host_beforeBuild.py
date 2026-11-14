# Firmware is input to the experimental braich image, not the host's EDK2.
if is_braich():
    firmware = env("VM_BIOS")
    expected = "3aa554094ffe1d86d7f9637e548d07df804f5034c32ac3da542ee8da6e2e783e"
    if not os.path.exists(firmware):
        download("https://downloads.omnios.org/media/braich/u-boot.bin", firmware)
    if _sha256_file(firmware) != expected:
        raise RuntimeError("braich U-Boot SHA256 mismatch")
