#!/usr/bin/env python3
"""
Indian eSign — STEP 2 of 2: EMBED  (ATick).

Reads the EsignResp XML your ESP returned, takes the <DocSignature> (and <UserX509Certificate> for
rawrsa), and embeds it into the prepared PDF.

    pkcs7 / pkcs7Pdf / pkcs7complete : <DocSignature> IS the CMS  -> base64-decode -> atick.embed
    rawrsa                           : <DocSignature> is the raw RSA signature, <UserX509Certificate>
                                       is the signer cert         -> atick.embed_rawrsa

pkcs7Pdf / pkcs7complete already carry the full chain + CRL/OCSP (pdfRevocationInfoArchival) AND a
signature timestamp from the CA, so the embedded signature is fully LTV + timestamped out of the box
— just embed it, nothing else to add. (For a `rawrsa` / plain `pkcs7` response that lacks them, add
`atick.add_doctimestamp(signed)` / your own LTV here.)

    python esign_embed.py <esign_response.xml>
    (defaults to the most recent esignrespxml_*.xml beside the project)
"""
import base64
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

import atick

HERE = os.path.dirname(os.path.abspath(__file__))
SIGNED = os.path.join(HERE, "..", "signed"); os.makedirs(SIGNED, exist_ok=True)
PREPARED = os.path.join(HERE, "esign_prepared.pdf")
META = os.path.join(HERE, "esign_meta.json")
OUT = os.path.join(SIGNED, "esign_complete.pdf")

# the ESP response XML: from argv, else the newest esignrespxml_*.xml under d:\project\python
if len(sys.argv) > 1:
    RESPONSE_XML = sys.argv[1]
else:
    cands = sorted(glob.glob(os.path.join(HERE, "..", "..", "..", "esignrespxml_*.xml")), key=os.path.getmtime)
    RESPONSE_XML = cands[-1] if cands else "esign_response.xml"

prepared = open(PREPARED, "rb").read()
meta = json.load(open(META))
rtype = meta["response_sig_type"]
hash_algo = meta["hash_algo"]


def _text(root, tag):
    """Find an element by local name (ignore any namespace) and return its stripped text."""
    for el in root.iter():
        if el.tag.split("}")[-1] == tag and (el.text or "").strip():
            return el.text.strip()
    return None


root = ET.fromstring(open(RESPONSE_XML, "rb").read())
status = root.get("status")
if status != "1":
    sys.exit(f"ESP returned failure: status={status} errCode={root.get('errCode')} errMsg={root.get('errMsg')}")
doc_sig_b64 = _text(root, "DocSignature")
if not doc_sig_b64:
    sys.exit("no <DocSignature> in the response")
doc_sig = base64.b64decode(doc_sig_b64)
print(f"response: txn={root.get('txn')} status=OK  DocSignature={len(doc_sig)} bytes")

# EMBED the ESP signature into the prepared PDF. For pkcs7Pdf / pkcs7complete the LTV revocation
# and the CA signature timestamp are already inside the CMS, so embedding completes the signature.
if rtype == "rawrsa":
    user_cert = base64.b64decode(_text(root, "UserX509Certificate"))
    signed = atick.embed_rawrsa(prepared, doc_sig, user_cert, chain=[], hash_algo=hash_algo)
else:                                              # pkcs7 / pkcs7Pdf / pkcs7complete: a full CMS
    signed = atick.embed(prepared, doc_sig)

open(OUT, "wb").write(signed)
print(f"eSigned PDF -> {OUT}  ({len(signed)} bytes)  [responseSigType={rtype}]")
