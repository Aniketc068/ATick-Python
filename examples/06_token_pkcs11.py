#!/usr/bin/env python3
"""
ATick — Example 06: Sign with a USB token / smart card / HSM (PKCS#11), on several pages.

The token does the crypto; the private key never leaves the device. You give the vendor PKCS#11
.dll, the PIN, and the hex serial of the signing certificate. The signer's name (CN) from the
token certificate is shown automatically in the appearance.

    python 06_token_pkcs11.py

Edit DLL / PIN below for your token. `atick.pkcs11_list(dll, pin)` discovers the serials.
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")

DLL = r"C:\Windows\System32\SignatureP11.dll"   # your token's PKCS#11 library
PIN = "12345678"

# 1) list certificates on the token (serial, CN)
certs = atick.pkcs11_list(DLL, PIN)
print("certificates on the token:")
for serial, cn in certs:
    print(f"  serial={serial}  CN={cn}")
if not certs:
    raise SystemExit("no certificates found on the token")
serial = certs[0][0]   # use the first one (or pick a specific serial)

# 2) sign with it on several pages at custom coordinates (CN auto-filled from the token cert)
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]
signed = atick.sign_pkcs11(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    dll=DLL, pin=PIN, serial=serial,
    style=atick.Style(reason="Signed with USB token"),   # default ATick logo
    placements=PLACEMENTS, mode="single", pades=True,
    # ltv=True, lta=True,        # optional LTV / archive timestamp
    # certify=atick.Certify.NO_CHANGES, lock_fields=["*"],   # optional certify / lock
    # verify=True, trusted_roots=["<root sha1>"],            # optional pre-sign checks
)
out = os.path.join(SIGNED, "06_token.pdf")
open(out, "wb").write(signed)
print(f"signed on {len(PLACEMENTS)} pages -> {out}  ({len(signed)} bytes)")
