#!/usr/bin/env python3
"""
ATick — Example 10: Password-protected PDFs (input and/or output) with a VALID signature.

ATick signs AFTER encrypting (and leaves the signature value unencrypted, as the PDF spec
requires), so the signature stays valid inside a password-protected file.

    open_password=...      the INPUT is password-protected -> decrypt it before signing
    encrypt_password=...   the OUTPUT is password-protected (user/open password)
    owner_password=...     optional owner (permissions) password for the output

There is also a standalone `atick.decrypt(pdf, password)` to turn an encrypted PDF into plaintext.
(Encrypted output is for the base signature — B-B / B-T; not combined with LTV/LTA.)

    python 10_encrypted.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]

# sign AND password-protect the output — the signature remains valid
signed = atick.sign_pfx(
    pdf, pfx=pfx, password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved"),
    placements=PLACEMENTS, mode="single", pades=True,
    encrypt_password="open123",       # password needed to OPEN the signed PDF
    owner_password="owner456",        # optional owner/permissions password
)
out = os.path.join(SIGNED, "10_signed_encrypted.pdf")
open(out, "wb").write(signed)
print(f"signed + password-protected -> {out}  (open with 'open123')")

# if your INPUT is already password-protected, sign it directly with open_password=...:
#   signed = atick.sign_pfx(encrypted_pdf, pfx=pfx, password="ABC12", style=..., placements=...,
#                           open_password="input_pw")
# or decrypt it first:
#   plain = atick.decrypt(encrypted_pdf, "input_pw")
