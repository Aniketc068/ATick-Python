#!/usr/bin/env python3
"""
ATick — FAST signing (revocation cache).

Fast signing is ON by default. With LTV on, the first signature fetches the certificate's CRL/OCSP
over the network; ATick then caches that revocation in-process, so every later signature with the
SAME certificate reuses it instead of re-fetching — a big speed-up when you sign many documents
(or add many signatures) in one run. (Timestamps are never cached — each one must be unique.)

    atick.set_fast_signing(True)     # default — reuse cached revocation for the same cert
    atick.set_fast_signing(False)    # always fetch fresh (turns the cache off + clears it)
    atick.clear_revocation_cache()   # forget cached revocation (e.g. after changing certificate)

    python fast_signing.py
"""
import os
import time
import logging

import atick

logging.disable(logging.CRITICAL)

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
pdf = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
PLACEMENTS = [(1, (40, 640, 300, 750)), (2, (320, 380, 560, 490)), (3, (180, 70, 430, 180))]

N = 5   # how many B-LT signatures to time


def sign_n(fast):
    atick.set_fast_signing(fast)
    atick.clear_revocation_cache()                 # start each run from a cold cache
    t0 = time.time()
    out = pdf
    for _ in range(N):
        out = atick.sign_pfx(pdf, pfx=pfx, password="ABC12",
                             style=atick.Style(cn="DS TEST CERTIFICATE 06", reason="Approved", green_tick=True),
                             placements=PLACEMENTS, mode="single", pades=True, ltv=True)
    return time.time() - t0, out


print(f"signing {N} B-LT documents (3 pages each) with the SAME certificate ...")
t_off, _ = sign_n(False)
t_on, last = sign_n(True)
open(os.path.join(SIGNED, "fast_signed.pdf"), "wb").write(last)

print(f"  fast signing OFF (fetch every time): {t_off:5.1f} s")
print(f"  fast signing ON  (cached revocation):{t_on:5.1f} s")
if t_on > 0:
    print(f"  -> {t_off / t_on:.1f}x faster")
print(f"  sample -> {os.path.join(SIGNED, 'fast_signed.pdf')}")
