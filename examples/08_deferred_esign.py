#!/usr/bin/env python3
"""
ATick — Example 08: Deferred (two-step) signing for a REMOTE key (eSign ESP / HSM / smart card),
shown on several pages.

When the private key lives elsewhere, ATick splits signing into two steps:

    1) atick.prepare_deferred_multi(pdf, style, placements, ...) -> (prepared_pdf, ctx)
         ctx["data"]   = the exact bytes that must be signed (the ByteRange)
         ctx["digest"] = their hash (send this to your eSign service if it wants a hash)
    2) your signer produces a DETACHED PKCS#7/CMS over ctx["data"]
    3) atick.embed(prepared_pdf, cms)                            -> signed_pdf

`prepare_deferred_multi` is the multi-page form (one signature, several placements). Below, ATick
itself (atick.cms_pfx) stands in for the external signer so the demo runs with no extra packages —
replace that block with YOUR eSign ESP / HSM / token call (it just returns a detached CMS over
ctx["data"]).

    python 08_deferred_esign.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
OUT = os.path.join(SIGNED, "08_deferred.pdf")

# ---- STEP 1: prepare (no key needed) -> appearance on every page + bytes-to-sign ----
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]
prepared, ctx = atick.prepare_deferred_multi(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    atick.Style(cn="DS TEST CERTIFICATE 06", reason="eSign"),   # default ATick logo
    placements=PLACEMENTS, mode="single", field_name="Signature1",
    sub_filter="adbe.pkcs7.detached", signer_name="DS TEST CERTIFICATE 06",
)
print("STEP 1: hash to send to the signer:", ctx["digest"].hex())

# ---- STEP 2: the EXTERNAL signer makes a detached CMS over ctx["data"] ----
#   >>> Replace this whole block with your eSign ESP / HSM / token call. <<<
#   Here ATick itself stands in for the external signer (atick.cms_pfx makes a detached CMS over the
#   given bytes), so the demo runs with no extra packages. In production this CMS comes from the ESP.
pfx = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()
cms = atick.cms_pfx(ctx["data"], pfx, "ABC12", hash_algo="sha256")

# ---- STEP 3: embed the CMS ----
signed = atick.embed(prepared, cms)
open(OUT, "wb").write(signed)
print(f"signed on {len(PLACEMENTS)} pages -> {OUT}  ({len(signed)} bytes)")
