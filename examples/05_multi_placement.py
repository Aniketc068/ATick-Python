#!/usr/bin/env python3
"""
ATick — Example 05: One signature shown on several pages / custom coordinates.

`placements` is a list of (page, (x1, y1, x2, y2)) — the signature appearance is drawn at each.
`mode` controls how the viewer's signature panel shows them:

    mode="single"  ONE signature, shown at every placement   -> panel shows 1 signature (Rev 1)
    mode="shared"  N fields sharing the one signature value   -> panel shows N entries, all Rev 1

(For N *independent* signatures — Rev 1, Rev 2, Rev 3 — sign repeatedly, one per placement.)

    python 05_multi_placement.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()   # a 3-page PDF
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
style = lambda: atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved", image=os.path.join(SAMPLES, "sign.png"))

# custom page + custom coordinates for each appearance
PLACEMENTS = [(1, (40, 660, 270, 770)), (2, (330, 380, 560, 490)), (3, (170, 60, 400, 170))]

for mode in ("single", "shared"):
    signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style(),
                            placements=PLACEMENTS, mode=mode, pades=True)
    out = os.path.join(SIGNED, f"05_{mode}.pdf")
    open(out, "wb").write(signed)
    print(f"mode={mode:6} -> {os.path.basename(out)}  (1 signature, {len(PLACEMENTS)} appearances)")
