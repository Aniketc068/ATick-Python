# Signing methods

ATick signs with three kinds of key holders. All three take the same options.

## 1. PFX / P12 / PEM file

```python
atick.sign_pfx(pdf, pfx=pfx_bytes, password="••••", style=…, placements=…)
```

`sign_pfx` accepts both **PKCS#12** (`.pfx`/`.p12`) and **PEM** — an unencrypted PKCS#8/PKCS#1
private key plus one or more `CERTIFICATE` blocks. The format is auto-detected, so a PEM works in
the same call (pass its bytes as `pfx=` and `password=""`):

```python
pem = open("signer.pem", "rb").read()
atick.sign_pfx(pdf, pfx=pem, password="", style=…, placements=…)
```

## 2. USB token / smart-card / HSM (PKCS#11)

```python
for serial, name in atick.pkcs11_list(dll="C:/Windows/System32/eps2003csp11.dll", pin="••••"):
    print(serial, name)

atick.sign_pkcs11(pdf, dll="…/lib.dll", pin="••••", serial="<hex serial>", style=…, placements=…)
```

The vendor PKCS#11 library (`.dll`/`.so`/`.dylib`) is loaded at run time — no C toolchain needed.

## 3. Windows certificate store

```python
atick.sign_winstore(pdf, style=…, placements=…)                 # opens the certificate picker
atick.sign_winstore(pdf, style=…, placements=…, thumbprint="<hex>")   # pick by thumbprint
```

## Common options

| Option | Meaning |
|---|---|
| `pades=True` | PAdES (`ETSI.CAdES.detached`); `False` → plain CMS (`adbe.pkcs7.detached`) |
| `hash_algo="sha256"` | `"sha256"`, `"sha384"`, `"sha512"` (signature is RSA PKCS#1 v1.5) |
| `timestamp=True` | add an RFC-3161 signature timestamp (B-T) |
| `tsa_url=`, `tsa_auth=(user, pass)` | choose / authenticate the timestamp authority |
| `ltv=True` | embed long-term validation (B-LT) |
| `lta=True` | add a document timestamp (B-LTA) |
| `certify=`, `lock_fields=` | [certification & locking](certification.md) |
| `verify=True`, `trusted_roots=[sha1, …]` | pre-sign expiry / CRL / OCSP / chain checks |
| `field_name="…"` | the signature field name (auto-uniquified — `Atick_1`, `Atick_2`, …) |
| `mode="single" \| "shared"` | one signature on many pages, or many fields sharing one value |

`sign_pfx` additionally accepts `open_password=` (decrypt an encrypted input), `encrypt_password=`
and `owner_password=` (password-protect the output).

## Multi-signatory (sign an already-signed PDF)

ATick signs as an **incremental update**: existing signatures keep their byte ranges and stay valid.
Just sign the already-signed PDF again; the field name is auto-uniquified so it never collides.

```python
signed_v1 = atick.sign_pfx(pdf,        pfx=pfx, password="••••", style=…, placements=…)   # Atick_1
signed_v2 = atick.sign_pfx(signed_v1,  pfx=pfx, password="••••", style=…, placements=…)   # Atick_2
```
