#!/usr/bin/env python3
"""
ATick — green tick (the validity-driven "?" mark).

`green_tick=True` embeds the "?" mark in the layered Acro6 appearance. Adobe then REPAINTS it
according to the signature's real validity:
    valid + trusted certificate  -> green check
    validity unknown / untrusted -> the "?"
    invalid / revoked / tampered -> red cross
So for a TRUSTED, valid certificate this shows a green tick in Adobe — and correctly turns red if
the signature is bad. (To force a green tick regardless of validity, use always_green_tick.py.)

    python green_tick.py   ->  signed/green_tick.pdf
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]

signed = atick.sign_pfx(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    pfx=open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read(), password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", org="Acme Corp", reason="Approved",
                      green_tick=True),                        # <-- "?" -> Adobe greens it if valid+trusted
    placements=PLACEMENTS, mode="single", pades=True,
)
out = os.path.join(SIGNED, "green_tick.pdf")
open(out, "wb").write(signed)
print(f"green tick (validity-driven) -> {out}")
