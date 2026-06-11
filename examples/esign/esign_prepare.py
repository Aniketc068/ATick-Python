#!/usr/bin/env python3
"""
Indian eSign — STEP 1 of 2: PREPARE  (ATick + managex-xml-sdk).

Builds the multi-page signature appearance + an empty container, computes the document hash, builds
the eSign request XML, and signs THAT request with managex-xml-sdk (the ASP's mapped certificate).

Outputs (between this step and STEP 2 you POST the request to your ESP and collect the response):
    esign_prepared.pdf          PDF with an empty signature container (do NOT modify it)
    esign_request_signed.xml    the signed eSign request -> POST to the ESP (multipart/form-data)
    esign_meta.json             internal: bytes-to-sign + hash algorithm (used by STEP 2)

Works for every eSign API version — edit the <Esign ...> attributes for your version; the hash,
the request signature, and the embed are identical across versions.

    python esign_prepare.py
"""
import base64
import json
import os
import datetime

import atick
import managex_xml_sdk as mx
from managex_xml_sdk.models.certificate_models import PFXConfig, ValidationConfig

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "..", "samples")
PFX = os.path.join(SAMPLES, "ABC12.pfx")
PW = "ABC12"
ROOTS = os.path.join(SAMPLES, "root_certificates")        # the ASP's trusted CA roots (for managex)
PREPARED = os.path.join(HERE, "esign_prepared.pdf")
REQUEST = os.path.join(HERE, "esign_request_signed.xml")
META = os.path.join(HERE, "esign_meta.json")

HASH_ALGO = "sha256"
RESPONSE_SIG_TYPE = "pkcs7Pdf"   # rawrsa | pkcs7 | pkcs7Pdf | pkcs7complete

# 1) PREPARE the PDF: signature box on every page (single signature), certified CFA so the later
#    document-timestamp does NOT invalidate it, with the ATick green-tick appearance.
PLACEMENTS = [(1, (40, 640, 300, 750)), (2, (320, 380, 560, 490)), (3, (180, 70, 430, 180))]
prepared, ctx = atick.prepare_deferred_multi(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    atick.Style(cn="DS TEST CERTIFICATE 06", org="Acme Corp", reason="eSign Approved", green_tick=True),
    PLACEMENTS, mode="single", field_name="ESignSignature",
    sub_filter="adbe.pkcs7.detached", certify=atick.Certify.FORM_FILLING_ANNOTATIONS,
    contents_size=60000, hash_algo=HASH_ALGO,
)
data = bytes(ctx["data"])
input_hash_hex = bytes(ctx["digest"]).hex()
print(f"document hash (InputHash, {HASH_ALGO} hex): {input_hash_hex}")

# 2) BUILD the eSign request XML (API v2.1 shown — adjust attributes for your ESP's version)
ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
request_xml = (
    f'<Esign ver="2.1" sc="Y" ts="{ts}" txn="TXN0003" ekycId="" ekycIdType="A" '
    f'aspId="impressionaspid" AuthMode="1" responseSigType="{RESPONSE_SIG_TYPE}" '
    f'responseUrl="https://test.esign.network/demo/2.1/getdocs/"><Docs>'
    f'<InputHash id="1" hashAlgorithm="{HASH_ALGO.upper()}" docInfo="Agreement Document">{input_hash_hex}</InputHash>'
    f'</Docs></Esign>')

# 3) SIGN the request XML with managex-xml-sdk (enveloped W3C XML-DSig, the ASP's certificate)
vc = ValidationConfig(check_validity=False, check_revocation_crl=False, check_revocation_ocsp=False,
                      trusted_roots_folder=ROOTS, require_key_usage_for_signing=False)
signer = mx.PFXSigner(PFXConfig(method="pfx", pfx_file=PFX, password=PW, validation_config=vc))
params = mx.SignatureEnvelopeParameters(
    signature_info=mx.SignatureInfo(canonicalization_algorithm=mx.CanonicalizationAlgorithm.C14N_OMIT_COMMENTS,
                                    signature_algorithm=mx.SignatureAlgorithm.RSA_SHA256),
    reference_info=mx.ReferenceInfo(uri="", digest_algorithm=mx.DigestAlgorithm.SHA256,
                                    transforms=[mx.TransformAlgorithm.ENVELOPED_SIGNATURE]),
    key_info=mx.KeyInfo(include_subject_name=True, include_certificate=True))
signed_request = signer.sign_xml_content(request_xml.encode("utf-8"), params)
if isinstance(signed_request, bytes):
    signed_request = signed_request.decode("utf-8")

# 4) SAVE — POST esign_request_signed.xml to the ESP, then run esign_embed.py with the response
open(PREPARED, "wb").write(prepared)
open(REQUEST, "w", encoding="utf-8").write(signed_request)
json.dump({"data_b64": base64.b64encode(data).decode(), "hash_algo": HASH_ALGO,
           "response_sig_type": RESPONSE_SIG_TYPE}, open(META, "w"))
print(f"prepared PDF       -> {PREPARED}")
print(f"signed request XML -> {REQUEST}   (POST this to your ESP)")
print(f"meta               -> {META}")
