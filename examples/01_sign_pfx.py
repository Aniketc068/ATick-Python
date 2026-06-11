#!/usr/bin/env python3
"""
ATick — Example 01: Sign a PDF with a .pfx / .p12 file (the simplest path).

`atick.sign_pfx()` does everything in one call: builds the verified-signature appearance, signs
the document, and writes the signed PDF. No other library is needed. Here the SAME signature is
shown on several pages, each at its own custom coordinates (mode="single" -> the viewer's panel
still shows it as one signature).

    python 01_sign_pfx.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
OUT = os.path.join(SIGNED, "01_pfx.pdf")

# place the appearance on more than one page, at custom coordinates: [(page, (x1, y1, x2, y2)), ...]
PLACEMENTS = [
    (1, (40, 640, 260, 750)),    # page 1, top-left
    (2, (330, 380, 560, 490)),   # page 2, middle-right
    (3, (180, 60, 400, 170)),    # page 3, bottom-centre
]

signed = atick.sign_pfx(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),   # a 3-page PDF
    pfx=open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read(),
    password="ABC12",
    style=atick.Style(
        cn="DS TEST CERTIFICATE 06",
        reason="Approved",
        # image not given -> ATick's default logo is used. image=False -> no logo. image="x.png" -> your own.
    ),
    placements=PLACEMENTS,
    mode="single",      # one signature, shown at every placement
    pades=True,
)

open(OUT, "wb").write(signed)
print(f"signed on {len(PLACEMENTS)} pages -> {OUT}  ({len(signed)} bytes)")
