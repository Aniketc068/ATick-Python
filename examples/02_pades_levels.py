#!/usr/bin/env python3
"""
ATick — Example 02: PAdES baseline levels B-B / B-T / B-LT / B-LTA (signed on several pages).

    B-B   = basic signature (pades=True)
    B-T   = + RFC-3161 signature timestamp        (timestamp=True)
    B-LT  = + DSS / LTV validation material        (ltv=True)
    B-LTA = + archive document timestamp           (lta=True)

Timestamp authority: `timestamp=True` uses the built-in default TSA (with a public fallback), or
set `tsa_url="https://your-tsa"` and `tsa_auth=("user","pass")`. Needs internet (TSA + CRL fetches).

    python 02_pades_levels.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
style = lambda: atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved")   # default ATick logo
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]

levels = {
    "B_B":   dict(pades=True),
    "B_T":   dict(pades=True, timestamp=True),
    "B_LT":  dict(pades=True, timestamp=True, ltv=True),
    "B_LTA": dict(pades=True, timestamp=True, lta=True),   # lta implies ltv + a doc-timestamp
}
for name, kw in levels.items():
    out = os.path.join(SIGNED, f"02_pades_{name}.pdf")
    signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style(),
                            placements=PLACEMENTS, mode="single", **kw)
    open(out, "wb").write(signed)
    print(f"PAdES-{name.replace('_', '-'):6} -> {os.path.basename(out)}  ({len(signed)} bytes, {len(PLACEMENTS)} pages)")
