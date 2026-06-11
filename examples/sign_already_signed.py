#!/usr/bin/env python3
"""
ATick — add a signature to an ALREADY-SIGNED PDF (multi-signatory / sequential signing).

ATick signs as an INCREMENTAL update: it only appends a new revision (the new field + signature),
never rewriting the bytes the earlier signatures cover. So every existing signature stays valid and
the new one is valid too. Just call sign_pfx on the signed PDF with a NEW, unique field_name.

    python sign_already_signed.py [input.pdf]      # default: d:/project/python/blank.pdf
"""
import io
import os
import sys
import logging

import atick

logging.disable(logging.CRITICAL)

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

INPUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SAMPLES, "signed.pdf")
pdf = open(INPUT, "rb").read()
n = pdf.count(b"/ByteRange")                       # signatures already present
print(f"input: {INPUT}   ({n} existing signature(s))")

# Add a NEW signature. Because this is an incremental update, the existing signature(s) keep their
# original byte ranges and stay valid; the new one is valid as well. The field name is auto-
# uniquified by ATick (default Atick_1 -> Atick_2 -> ... on each re-sign), so it never collides —
# pass field_name="YourName" only if you want a specific one.
signed = atick.sign_pfx(
    pdf, pfx=pfx, password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", org="Acme Corp",
                      reason="Counter-signature", green_tick=True),
    placements=[(1, (40, 60, 300, 170))],          # a free spot for the new appearance
    pades=True, timestamp=True,                    # field_name defaults to Atick_1 (auto-uniquified)
)
out = os.path.join(SIGNED, "added_signature.pdf")
open(out, "wb").write(signed)
total = signed.count(b"/ByteRange")
print(f"added Signature{n + 1} -> {out}   ({len(signed)} bytes)")
print(f"the document now has {total} signature(s): the {n} existing one(s) are untouched (their byte")
print("ranges are unchanged by the incremental update) and all stay valid — open it in Adobe to verify.")
