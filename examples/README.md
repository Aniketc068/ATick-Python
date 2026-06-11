# ATick — examples

Self-contained. Inputs live in `../samples/`, every script writes its signed PDF into
`./signed/`. Nothing here depends on any folder outside `atick-standalone/`.

```bash
pip install atick
cd examples
python 01_sign_pfx.py          # -> signed/01_pfx.pdf
```

| # | Script | Use case | Output(s) in `signed/` |
|---|--------|----------|------------------------|
| 01 | `01_sign_pfx.py` | sign with a `.pfx` (one call) | `01_pfx.pdf` |
| 02 | `02_pades_levels.py` | PAdES **B-B / B-T / B-LT / B-LTA** | `02_pades_*.pdf` |
| 03 | `03_appearance.py` | full appearance (`atick.Style`) | `03_appearance.pdf` |
| 04 | `04_certify_and_lock.py` | DocMDP certification + field lock | `04_certified_*.pdf` |
| 05 | `05_multi_placement.py` | one signature, many pages (single/shared) | `05_single.pdf`, `05_shared.pdf` |
| 06 | `06_token_pkcs11.py` | USB token / smart card / HSM (PKCS#11) | `06_token.pdf` |
| 07 | `07_windows_store.py` | Windows store (certificate picker) | `07_winstore.pdf` |
| 08 | `08_deferred_esign.py` | deferred 2-step (remote key) | `08_deferred.pdf` |
| 09 | `09_verify_certificate.py` | pre-sign checks: expiry / CRL / OCSP / trusted-root | `09_verified.pdf` |
| 10 | `10_encrypted.py` | password-protected input/output, valid signature | `10_signed_encrypted.pdf` |
| 11 | `11_mark_color.py` | "?" mark colour + gradient | `11_mark_*.pdf` |
| 12 | `12_metadata.py` | document metadata (`set_metadata`) | `12_metadata.pdf` |
| 13 | `13_hash_algorithms.py` | SHA-256 / 384 / 512 | `13_hash_*.pdf` |
| 14 | `14_field_api.py` | low-level field API (prepare / sign_field / prepare_fields) | `14_*.pdf` |
| — | `esign/esign_prepare.py` + `esign_embed.py` | **Indian eSign (CCA eSign API v2.1)** — rawrsa / PKCS7 / PKCS7pdf / PKCS7complete | `esign_rawrsa.pdf`, `esign_pkcs7.pdf` |

## The three signing methods

```python
atick.sign_pfx(pdf, pfx=..., password=..., style=..., placements=...)            # .pfx / .p12
atick.sign_pkcs11(pdf, dll=..., pin=..., serial=..., style=..., placements=...)  # USB token / HSM
atick.sign_winstore(pdf, style=..., placements=..., thumbprint=None)             # Windows store
```

Common options (all three): `pades=True`, `hash_algo="sha256|sha384|sha512"`, `timestamp=True`,
`tsa_url=`, `tsa_auth=(user,pass)`, `ltv=True`, `lta=True`, `certify=atick.Certify.NO_CHANGES`,
`lock_fields=["*"]`, `verify=True`, `trusted_roots=[...]`, plus on `sign_pfx`: `open_password=`,
`encrypt_password=`, `owner_password=`. Errors raise `atick.AtickError`.

All example outputs validate with an intact signature (run them and check `signed/`).
