# Indian eSign (CCA)

ATick supports the CCA eSign Online Electronic Signature Service for **every API version** (v1.x …
v3.x). The flow is the same across versions — only the request XML attributes differ.

```
PDF  ->  SHA-256 of the ByteRange (the InputHash, hex)
     ->  build the <Esign …> request XML for your version, put the InputHash in <InputHash>
     ->  sign the request XML (your managex-xml-sdk)            [enveloped W3C XML-DSig]
     ->  POST it (multipart/form-data) to the ESP
     ->  EsignResp -> <DocSignature> (rawrsa / pkcs7 / pkcs7Pdf / pkcs7complete)
     ->  embed it into the PDF
```

## Step 1 — prepare + hash

```python
prepared, ctx = atick.prepare_deferred_multi(
    pdf, atick.Style(cn="…", always_check=True),
    [(1, (40, 640, 300, 750)), (2, (320, 380, 560, 490))],   # signature box on each page
    mode="single", sub_filter="adbe.pkcs7.detached",
    certify=atick.Certify.FORM_FILLING_ANNOTATIONS,          # CFA -> later timestamp won't invalidate
    contents_size=60000,                                     # room for chain + revocation + timestamp
)
input_hash_hex = bytes(ctx["digest"]).hex()                  # goes into <InputHash>
data = bytes(ctx["data"])                                    # the exact bytes the ESP signs
```

## Step 2 — sign the request XML with `managex-xml-sdk`

```{important}
**`managex-xml-sdk` needs a trusted-roots folder.** Before it will sign, it validates your ASP
certificate against the CA root certificate(s) in the folder you give as
`ValidationConfig(trusted_roots_folder=…)`. That folder **must exist and contain the CA root
certificate(s) as PEM files** — if the folder is missing or empty, signing the request **fails and
eSign will not work**. Put your CA's root (and intermediate) certificates there as `.pem` files.
```


```python
import managex_xml_sdk as mx
from managex_xml_sdk.models.certificate_models import PFXConfig, ValidationConfig

request = (f'<Esign ver="2.1" sc="Y" ts="…" txn="TXN1" ekycIdType="A" aspId="…" AuthMode="1" '
           f'responseSigType="pkcs7Pdf" responseUrl="https://…/"><Docs>'
           f'<InputHash id="1" hashAlgorithm="SHA256" docInfo="Agreement">{input_hash_hex}</InputHash>'
           f'</Docs></Esign>')

signer = mx.PFXSigner(PFXConfig(method="pfx", pfx_file="asp.pfx", password="…",
                                validation_config=ValidationConfig(trusted_roots_folder="roots")))
params = mx.SignatureEnvelopeParameters(
    signature_info=mx.SignatureInfo(signature_algorithm=mx.SignatureAlgorithm.RSA_SHA256),
    reference_info=mx.ReferenceInfo(uri="", transforms=[mx.TransformAlgorithm.ENVELOPED_SIGNATURE]),
    key_info=mx.KeyInfo(include_subject_name=True, include_certificate=True))
signed_request = signer.sign_xml_content(request.encode(), params)   # POST this to the ESP
```

## Step 3 — embed the ESP response

```python
import base64, xml.etree.ElementTree as ET
root = ET.fromstring(esign_response_xml)
doc_sig = base64.b64decode(next(e.text for e in root.iter() if e.tag.endswith("DocSignature")))

signed = atick.embed(prepared, doc_sig)                # pkcs7 / pkcs7Pdf / pkcs7complete (a full CMS)
# rawrsa: atick.embed_rawrsa(prepared, doc_sig, user_cert)
```

`pkcs7Pdf` and `pkcs7complete` responses already carry the full chain, the revocation (under
`pdfRevocationInfoArchival`) and a CA timestamp — so the embedded signature is LTV-complete and
timestamped out of the box.

## `responseSigType`

| Value | Returns | Embed with |
|---|---|---|
| `rawrsa` | a raw RSA signature + the signer cert | `atick.embed_rawrsa` |
| `pkcs7` | a CMS, signer cert only (no revocation) | `atick.embed` |
| `pkcs7Pdf` | a CMS, full chain + CRL/OCSP (signed attr) + timestamp | `atick.embed` |
| `pkcs7complete` | a CMS, full chain + revocation (unsigned attr) | `atick.embed` |

## Simulating the ESP for testing

`atick.cms_pfx(data, pfx, pw, revocation=True, timestamp=True)` produces a `pkcs7Pdf`-style CMS, and
`atick.sign_hash_pfx(data, pfx, pw)` a `rawrsa` response — so you can run the whole flow end-to-end
without a live ESP. See `examples/esign/`.

## Command line

```bash
atick esign-prepare in.pdf prepared.pdf --certify form-annots   # prints the InputHash
# sign the request XML (managex-xml-sdk) + POST to the ESP, save the response
atick esign-embed prepared.pdf response.xml signed.pdf
```
