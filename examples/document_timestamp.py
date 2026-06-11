#!/usr/bin/env python3
"""
ATick — add a DOCUMENT timestamp to an already-signed PDF.

A document timestamp (RFC-3161 DocTimeStamp) seals the WHOLE document with a trusted time from a
timestamping authority, independent of who signed it. With ltv=True it also embeds the TSA chain's
validation material into the DSS, taking a B-LT document up to PAdES B-LTA (long-term archival).

    atick.add_doctimestamp(pdf, tsa_url=None, tsa_auth=None, ltv=True)

Use it after embedding an eSign / deferred signature, or to archive-timestamp any signed PDF.

    python document_timestamp.py
"""
import os

import atick

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

# 1) a normal B-LT signature
signed = atick.sign_pfx(
    open(os.path.join(SAMPLES, "blank.pdf"), "rb").read(), pfx=pfx, password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved", green_tick=True),
    placements=[(1, (300, 55, 575, 175))], pades=True, timestamp=True, ltv=True,
)

# 2) seal the whole document with a trusted document timestamp (-> PAdES B-LTA)
final = atick.add_doctimestamp(signed)               # ltv=True (default) also covers the TSA chain

out = os.path.join(SIGNED, "document_timestamp.pdf")
open(out, "wb").write(final)
print(f"signature + document timestamp (B-LTA) -> {out}   ({len(final)} bytes)")
