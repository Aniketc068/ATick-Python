#!/usr/bin/env python3
"""
ATick — Example 13: Choose the signing hash (SHA-256 / SHA-384 / SHA-512).

The signature is RSA (per the certificate) with PKCS#1 v1.5; you pick the hash. Adobe's signature
properties then show e.g. "Hash Algorithm: SHA384" + "Signature Algorithm: RSA with PKCS#1 v1.5".

    python 13_hash_algorithms.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

for algo in ("sha256", "sha384", "sha512"):
    signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12",
                            style=atick.Style(cn="Signer", reason=algo.upper()),
                            placements=[(1, (300, 55, 575, 175))], pades=True, hash_algo=algo)
    out = os.path.join(SIGNED, f"13_hash_{algo}.pdf")
    open(out, "wb").write(signed)
    print(f"{algo} -> {os.path.basename(out)}")
