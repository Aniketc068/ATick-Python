#!/usr/bin/env python3
"""
ATick — Example 11: Colour of the "?" verified-signature mark (and gradient).

`mark_color` accepts any common Python colour; `mark_gradient` (2+ colours) fills the "?" with a
linear gradient instead. If you set neither, the default yellow "?" is used. (The green-tick /
red-cross that Adobe shows are the viewer's live validation icons — not part of the PDF.)

    python 11_mark_color.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
P = [(1, (300, 55, 575, 175))]

variants = {
    "default":  {},                                            # yellow "?"
    "hex":      dict(mark_color="#E53935"),                    # hex
    "named":    dict(mark_color="blue"),                       # CSS name
    "rgb255":   dict(mark_color=(255, 140, 0)),                # 0..255 ints
    "gradient": dict(mark_gradient=["red", "orange", "yellow"]),  # gradient
}
for name, kw in variants.items():
    signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12",
                            style=atick.Style(cn="Signer", reason=f"mark: {name}", **kw),
                            placements=P, pades=True)
    out = os.path.join(SIGNED, f"11_mark_{name}.pdf")
    open(out, "wb").write(signed)
    print(f"mark {name:9} -> {os.path.basename(out)}")
