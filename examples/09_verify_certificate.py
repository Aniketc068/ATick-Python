#!/usr/bin/env python3
"""
ATick — Example 09: OPTIONAL pre-signing certificate checks (security), on several pages.

Before signing, ATick can refuse to use a bad certificate. Turn the checks on; if any fails,
signing raises `atick.AtickError` and NO signature is produced.

    verify=True            -> certificate must be: not expired / not-yet-valid,
                              not revoked by its CRL, and not revoked by OCSP.
    trusted_roots=[...]     -> the certificate must chain up to a trusted anchor whose SHA-1
                              thumbprint is in this list. Missing issuer certificates are fetched
                              LIVE from each certificate's AIA caIssuers URL (so the chain is built
                              from the authority info, not just whatever the .pfx/token shipped).

These work on every signing path: sign_pfx, sign_pkcs11, sign_winstore.

    python 09_verify_certificate.py
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

# 1) full revocation + expiry checks
try:
    signed = atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style(), placements=PLACEMENTS,
                            mode="single", pades=True, verify=True)
    open(os.path.join(SIGNED, "09_verified.pdf"), "wb").write(signed)
    print("verify=True  -> certificate OK, signed on 3 pages -> out_09_verified.pdf")
except atick.AtickError as e:
    print("verify=True  -> refused:", e)

# 2) pin the trusted root (replace with YOUR CA root's SHA-1 thumbprint)
TRUSTED_ROOTS = ["4c16ee46bbc7ad6c7e28d068b7ab5fa734374e46"]   # example thumbprint
try:
    atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style(), placements=PLACEMENTS,
                   mode="single", pades=True, trusted_roots=TRUSTED_ROOTS)
    print("trusted_roots-> chain anchored to a pinned root, signed")
except atick.AtickError as e:
    print("trusted_roots-> refused:", e)

# 3) an untrusted root is refused
try:
    atick.sign_pfx(pdf, pfx=pfx, password="ABC12", style=style(), placements=PLACEMENTS,
                   mode="single", pades=True, trusted_roots=["00" * 20])
    print("untrusted    -> ERROR: should have been refused")
except atick.AtickError as e:
    print("untrusted    -> correctly refused:", str(e)[:60])
