#!/usr/bin/env python3
"""
ATick — Example 07: Sign with a certificate from the WINDOWS certificate store, on several pages.

With no thumbprint, a Windows certificate picker pops up ("ATick Digital Signature") so the
user chooses the certificate; its private key (CSP/KSP — token PIN prompt if it's a token) signs
the hash. The key never leaves the device. The chosen certificate's CN/O are shown automatically.

    python 07_windows_store.py            # shows the Windows picker
    python 07_windows_store.py THUMB      # use a specific thumbprint (no picker)

Windows only.
"""
import os
import sys
import atick

if atick.sign_winstore is None:
    raise SystemExit("sign_winstore is only available on Windows")

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
thumbprint = sys.argv[1] if len(sys.argv) > 1 else None   # None -> Windows picker dialog

PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]
signed = atick.sign_winstore(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    style=atick.Style(reason="Signed via Windows certificate store", text="Verified by ATick"),
    placements=PLACEMENTS, mode="single", thumbprint=thumbprint, pades=True,
    # ltv=True, lta=True, certify=atick.Certify.FORM_FILLING,   # optional
)
out = os.path.join(SIGNED, "07_winstore.pdf")
open(out, "wb").write(signed)
print(f"signed on {len(PLACEMENTS)} pages -> {out}  ({len(signed)} bytes)")
