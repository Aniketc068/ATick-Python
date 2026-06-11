# PAdES levels

ATick produces all four PAdES baseline levels. Adobe Acrobat shows the level in the advanced
signature properties.

| Level | Call | What it adds |
|---|---|---|
| **B-B** | `pades=True` | a PAdES (CAdES) signature with the ESS signing-certificate-v2 attribute |
| **B-T** | `+ timestamp=True` | an RFC-3161 signature timestamp |
| **B-LT** | `+ ltv=True` | the DSS: full chain + CRLs + OCSP responses + per-signature VRI |
| **B-LTA** | `+ lta=True` | a document timestamp over the whole file |

```python
atick.sign_pfx(pdf, pfx=…, password=…, style=…, placements=…, pades=True)                  # B-B
atick.sign_pfx(pdf, …, pades=True, timestamp=True)                                         # B-T
atick.sign_pfx(pdf, …, pades=True, timestamp=True, ltv=True)                               # B-LT
atick.sign_pfx(pdf, …, pades=True, timestamp=True, lta=True)                               # B-LTA
```

For **B-LT** ATick embeds the complete validation material (the signer chain, its CRLs and full
`OCSPResponse`s, the OCSP responder certificates, a per-signature VRI, and the `/Extensions /ESIC`
declaration) so Adobe reports **“PAdES Signature Level: B-LT”**.

## PAdES vs. plain CMS, and `/M`

- `pades=True` → SubFilter `ETSI.CAdES.detached`; the signature dictionary carries `/M` (signing
  time), which Adobe uses to classify the PAdES level.
- `pades=False` → SubFilter `adbe.pkcs7.detached`, a plain PKCS#7 signature with **no `/M`** (unless
  you pass `signing_time=`).

## Document timestamp on an existing signature

```python
final = atick.add_doctimestamp(signed_pdf)     # archive timestamp over the whole document (B-LTA)
```
