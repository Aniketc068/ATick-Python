#!/usr/bin/env python3
"""
ATick — custom date formats + signing with a PEM file.

DATE
    By default the appearance shows the current time as "10-Jun-2026 03:54 PM". Change it freely:
        date_format="…"   any Python strftime pattern, applied to the current time
        date="…"          a fixed string you provide (any text)
        date=""           no date line at all

    Common world formats (all via date_format):
        "%d-%b-%Y %I:%M %p"      10-Jun-2026 03:54 PM   (default)
        "%Y-%m-%d %H:%M:%S"      2026-06-10 15:54:21    (ISO-ish)
        "%d/%m/%Y %H:%M"         10/06/2026 15:54       (DD/MM/YYYY — India/EU)
        "%m/%d/%Y %I:%M %p"      06/10/2026 03:54 PM    (US)
        "%A, %d %B %Y"           Wednesday, 10 June 2026
        "%d.%m.%Y"               10.06.2026             (German)

PEM
    sign_pfx also accepts a PEM file (PKCS#8/PKCS#1 key + CERTIFICATE blocks) instead of a .pfx —
    the format is auto-detected, so the same call works for both.

    python 18_date_and_pem.py
"""
import os
import atick

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
pdf = open(os.path.join(SAMPLES, "blank.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

# --- different date formats ---
for tag, fmt in [("iso", "%Y-%m-%d %H:%M:%S"), ("eu", "%d/%m/%Y %H:%M"),
                 ("us", "%m/%d/%Y %I:%M %p"), ("words", "%A, %d %B %Y")]:
    signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12",
        style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved", date_format=fmt),
        placements=[(1, (300, 55, 575, 175))], pades=True)
    open(os.path.join(SIGNED, f"18_date_{tag}.pdf"), "wb").write(signed)
    print(f"date_format={fmt!r:24} -> 18_date_{tag}.pdf")

# a fixed custom date string
signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved", date="Signed on the 10th of June, 2026"),
    placements=[(1, (300, 55, 575, 175))], pades=True)
open(os.path.join(SIGNED, "18_date_custom.pdf"), "wb").write(signed)
print("date='Signed on the 10th…'       -> 18_date_custom.pdf")

# --- sign with a PEM file (same sign_pfx call; format auto-detected) ---
pem = open(os.path.join(SAMPLES, "ABC12.pem"), "rb").read()
signed = atick.sign_pfx(pdf, pfx=pem, password="",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Signed with a PEM", green_tick=True),
    placements=[(1, (300, 55, 575, 175))], pades=True)
open(os.path.join(SIGNED, "18_sign_pem.pdf"), "wb").write(signed)
print(f"signed with a PEM file            -> 18_sign_pem.pdf  ({len(signed)} bytes)")
