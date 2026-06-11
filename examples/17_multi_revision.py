#!/usr/bin/env python3
"""
ATick — multi-signature / multi-revision (rev1 -> rev2 -> rev3).

Each signature is an INCREMENTAL revision: signing again never touches the bytes the earlier
signatures cover, so every revision stays valid. This is how a document is signed by several people
in turn (approval signatures). Each signature here goes on its own page + has its own field name.

Produces three PDFs so you can see the chain grow:
    rev1.pdf  -> 1 signature
    rev2.pdf  -> 2 signatures (rev1 untouched + rev2)
    rev3.pdf  -> 3 signatures (rev1, rev2 untouched + rev3)

    python 17_multi_revision.py
"""
import os

import atick

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

# each revision: (field name, page + rectangle, reason)
REVS = [
    ("rev1", (1, (40, 640, 300, 750)), "First approval"),
    ("rev2", (2, (320, 380, 560, 490)), "Second approval"),
    ("rev3", (3, (180, 70, 430, 180)), "Third approval"),
]

doc = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()
for name, placement, reason in REVS:
    doc = atick.sign_pfx(
        doc, pfx=pfx, password="ABC12",
        style=atick.Style(cn="DS TEST CERTIFICATE 06", reason=reason, green_tick=True),
        placements=[placement], field_name=name, pades=True, timestamp=True,
    )
    out = os.path.join(SIGNED, f"{name}.pdf")
    open(out, "wb").write(doc)
    print(f"{name} -> {out}   ({doc.count(b'/ByteRange')} signature(s) so far)")
