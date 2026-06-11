#!/usr/bin/env python3
"""
ATick — without green tick (basic signature, no mark at all).

`green_tick=False` embeds NO mark and uses a FLAT appearance, so Adobe shows NOTHING extra — not
the "?", not a green tick, not even its own dynamic validity graphic. Just the logo + signer text.
A plain, basic signature. (The signature is still cryptographically valid and appears in Adobe's
Signature panel.)

    python without_green_tick.py   ->  signed/without_green_tick.pdf
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
                      green_tick=False),                       # <-- no mark, no Adobe overlay
    placements=PLACEMENTS, mode="single", pades=True,
)
out = os.path.join(SIGNED, "without_green_tick.pdf")
open(out, "wb").write(signed)
print(f"without green tick (basic) -> {out}")
