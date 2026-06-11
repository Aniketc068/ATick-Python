#!/usr/bin/env python3
"""
ATick — Example 14: Low-level field API.

    atick.prepare(pdf, style, page, rect, field_name)   -> add ONE empty signature field
    atick.sign_field(pdf, field_name, ...)              -> attach a container to that field,
                                                           returns (pdf, ctx) with bytes-to-sign
    atick.embed(pdf, cms)                               -> fill the container
    atick.prepare_fields(pdf, styles, placements, names)-> add SEVERAL empty fields at once

Useful when the field is created up front (e.g. a template) and signed later, possibly by a
remote key. Below, ATick itself (atick.cms_pfx) stands in for the external signer, so the demo runs
with no extra packages — in production that CMS comes from your remote key / HSM / eSign ESP.

    python 14_field_api.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
BLANK = open(os.path.join(SAMPLES, "blank.pdf"), "rb").read()
PAGES3 = open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read()
PFX = open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read()

def external_sign(byterange):
    # the external signer returns a detached CMS over `byterange`; here ATick produces it
    return atick.cms_pfx(byterange, PFX, "ABC12", hash_algo="sha256")

# 1) prepare ONE empty field -> sign it by name -> embed
staged = atick.prepare(BLANK, atick.Style(cn="Field Signer", reason="signed by name"),
                       page=1, rect=(300, 55, 575, 175), field_name="MyField")
prepared, ctx = atick.sign_field(staged, field_name="MyField", sub_filter="adbe.pkcs7.detached")
signed = atick.embed(prepared, external_sign(ctx["data"]))
open(os.path.join(SIGNED, "14_sign_field.pdf"), "wb").write(signed)
print("prepare + sign_field + embed -> 14_sign_field.pdf")

# 2) prepare SEVERAL empty fields at once (a template ready to be signed later)
template = atick.prepare_fields(PAGES3,
    styles=[atick.Style(cn="Field A"), atick.Style(cn="Field B"), atick.Style(cn="Field C")],
    placements=[[(1, (40, 640, 260, 750))], [(2, (330, 380, 560, 490))], [(3, (180, 60, 400, 170))]],
    names=["FieldA", "FieldB", "FieldC"])
open(os.path.join(SIGNED, "14_prepared_fields_template.pdf"), "wb").write(template)
print("prepare_fields (3 empty fields) -> 14_prepared_fields_template.pdf")
