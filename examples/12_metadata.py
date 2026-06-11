#!/usr/bin/env python3
"""
ATick — Example 12: Set the document metadata, then sign.

`atick.set_metadata()` writes the /Info fields on the UNSIGNED PDF (run it before signing). The
Producer stays ATick's branding; everything else is yours. `created` / `modified` take a PDF date
string "D:YYYYMMDDHHmmSS+HH'mm'". `application` maps to /Creator.

    python 12_metadata.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

# 1) set metadata on the unsigned PDF
pdf = atick.set_metadata(
    pdf,
    title="Agreement 2026",
    author="Aniket Chaturvedi",
    subject="Demonstration of metadata",
    keywords="dsc, esign, pades, atick",
    application="ATick",                              # -> /Creator
    created="D:20260609120000+05'30'",
    modified="D:20260609130000+05'30'",
)

# 2) sign it
signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12",
                        style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved"),
                        placements=[(1, (300, 55, 575, 175))], pades=True)
out = os.path.join(SIGNED, "12_metadata.pdf")
open(out, "wb").write(signed)
print(f"signed with metadata -> {out}  (check Title/Author/Subject/Keywords/Creator in the PDF properties)")
