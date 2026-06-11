#!/usr/bin/env python3
"""
ATick — create ONLY a signature container, WITH the ATick appearance (not a blank one).

Produces a PDF that already shows the verified-signature appearance (logo + signer text + the
green tick / "?" mark) and has an EMPTY signature container (/Contents placeholder) ready to be
filled later — by `atick.embed(...)`, by an eSign ESP response, or by any external signer that
signs a named field. Nothing is signed here; only the field + appearance + container are built.

    python make_container.py [input.pdf]      # default: ../samples/blank.pdf
"""
import os
import sys

import atick

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)

INPUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SAMPLES, "blank.pdf")
pdf = open(INPUT, "rb").read()

# Build the signature field + the ATick appearance + an EMPTY container (no signing).
prepared, ctx = atick.prepare_deferred_multi(
    pdf,
    atick.Style(cn="DS TEST CERTIFICATE 06", org="Acme Corp", reason="Approved", green_tick=True),
    [(1, (300, 55, 575, 175))],                 # where the appearance is drawn (page, rect)
    mode="single", field_name="Signature1",
    sub_filter="adbe.pkcs7.detached",           # "ETSI.CAdES.detached" for a PAdES container
    contents_size=16384,                        # size of the empty container (enlarge for LTV/chain)
)

out = os.path.join(SIGNED, "container.pdf")
open(out, "wb").write(prepared)
print(f"container (ATick appearance + empty signature) -> {out}   ({len(prepared)} bytes)")
print(f"field: {ctx['field']}   |   document hash ({ctx['algo']}) to sign: {bytes(ctx['digest']).hex()}")
print("Sign it later: atick.embed(prepared, cms)  /  atick.embed_rawrsa(prepared, raw_sig, cert)")
