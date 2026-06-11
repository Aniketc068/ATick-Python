#!/usr/bin/env python3
"""
ATick — Example 16: INVISIBLE signature.

An invisible signature is cryptographically present and valid, but draws NOTHING on any page —
no appearance, no logo, no mark. Adobe shows it in the Signature panel, but the document looks
unchanged. To create one, pass an EMPTY `placements=[]` (no appearance is built).

Works with every option (timestamp, LTV, certify, encryption, ...) — only the visible appearance
is omitted.

    python 16_invisible.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

# INVISIBLE: placements=[] -> no appearance is drawn, signature is still valid
signed = atick.sign_pfx(
    pdf, pfx=pfx, password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Invisible approval"),
    placements=[],                    # <-- empty -> invisible signature
    field_name="InvisibleSignature",
    pades=True, timestamp=True, ltv=True,
)
out = os.path.join(SIGNED, "16_invisible.pdf")
open(out, "wb").write(signed)
print(f"invisible signature (nothing drawn, signature valid) -> {out}")
