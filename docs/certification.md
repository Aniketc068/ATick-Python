# Certification & field locking

## Certification (DocMDP)

A **certifying** signature declares which later changes are allowed. Use `certify=` on the first
signature:

```python
from atick import Certify

atick.sign_pfx(pdf, …, certify=Certify.NO_CHANGES)               # P=1 — no changes at all
atick.sign_pfx(pdf, …, certify=Certify.FORM_FILLING)             # P=2 — form filling + signing
atick.sign_pfx(pdf, …, certify=Certify.FORM_FILLING_ANNOTATIONS) # P=3 — + annotations
atick.sign_pfx(pdf, …, certify=Certify.NONE)                     # 0 — a normal (non-certifying) signature
```

| Level | Value | Allows |
|---|---|---|
| `NONE` | 0 | a normal approval signature (no certification) |
| `NO_CHANGES` | 1 | nothing — any later change (incl. another signature, LTV, timestamp) breaks it |
| `FORM_FILLING` | 2 | filling form fields + adding signatures |
| `FORM_FILLING_ANNOTATIONS` | 3 | the above + annotations |

```{note}
`NO_CHANGES` (P=1) forbids **everything** afterwards — so it cannot be combined with later LTV,
document timestamps, or extra approval signatures. Use it as a single, final signature. For a
document that will gather more signatures, certify with `FORM_FILLING` / `FORM_FILLING_ANNOTATIONS`.
```

## Field locking (FieldMDP)

Lock specific form fields so they cannot be changed after signing — without certifying the whole
document:

```python
atick.sign_pfx(pdf, …, lock_fields=["ApproverName"])   # lock these fields
atick.sign_pfx(pdf, …, lock_fields=["*"])              # lock ALL fields
```

If a locked field is altered after signing, the signature is reported as invalid.

## Pre-sign checks

Validate the signing certificate **before** signing:

```python
atick.sign_pfx(pdf, …,
    verify=True,                                   # not expired + CRL + OCSP + not revoked
    trusted_roots=["<root SHA-1>", "<another>"],   # chain must reach one of these (built from AIA)
)
```
