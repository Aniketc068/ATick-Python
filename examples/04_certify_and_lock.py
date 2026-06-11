#!/usr/bin/env python3
"""
ATick — Example 04: Certification (DocMDP) + field locking (FieldMDP), shown on several pages.

A CERTIFYING signature locks what may change after it (Adobe shows a blue "Certified by…" bar):

    atick.Certify.NONE                      normal approval signature (no certification)
    atick.Certify.NO_CHANGES                no changes allowed at all (full lock)
    atick.Certify.FORM_FILLING              only form filling + further signing
    atick.Certify.FORM_FILLING_ANNOTATIONS  + annotations

Field locking marks form fields read-only after this signature:

    lock_fields=["*"]                       lock ALL fields
    lock_fields=["Signature2", "Amount"]    lock only these fields

    python 04_certify_and_lock.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
pdf = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
style = lambda r: atick.Style(cn="DS TEST CERTIFICATE 06", reason=r)   # default ATick logo
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]

# 1) certify "no changes allowed" + lock every field
signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style("Certified - no changes"),
                        placements=PLACEMENTS, mode="single", pades=True,
                        certify=atick.Certify.NO_CHANGES, lock_fields=["*"])
open(os.path.join(SIGNED, "04_certified_locked.pdf"), "wb").write(signed)
print("certified (NO_CHANGES) + all fields locked, 3 pages -> out_04_certified_locked.pdf")

# 2) certify "form filling allowed" only
signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style("Certified - form filling"),
                        placements=PLACEMENTS, mode="single", pades=True,
                        certify=atick.Certify.FORM_FILLING)
open(os.path.join(SIGNED, "04_certified_formfill.pdf"), "wb").write(signed)
print("certified (FORM_FILLING), 3 pages                   -> out_04_certified_formfill.pdf")
