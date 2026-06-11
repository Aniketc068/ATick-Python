# API reference

All functions raise `atick.AtickError` on failure.

## Signing

```{py:function} atick.sign_pfx(pdf, *, pfx, password, style, placements, mode="single", field_name="Atick_1", pades=True, hash_algo="sha256", timestamp=False, tsa_url=None, tsa_auth=None, ltv=False, lta=False, doc_tsa_url=None, doc_tsa_auth=None, reason=None, location=None, signing_time=None, signer_name=None, contents_size=0, certify=0, lock_fields=[], verify=False, trusted_roots=[], open_password=None, encrypt_password=None, owner_password=None, embed_revocation=True)
Sign `pdf` (bytes) with a PFX/P12. Returns the signed PDF (bytes).
```

```{py:function} atick.sign_pkcs11(pdf, *, dll, pin, serial, style, placements, ...)
Sign with a PKCS#11 token / smart-card / HSM. Same options as `sign_pfx` (no PFX/encryption args).
```

```{py:function} atick.sign_winstore(pdf, *, style, placements, thumbprint=None, ...)
Sign with a certificate from the Windows store. `thumbprint=None` opens the certificate picker.
```

```{py:function} atick.pkcs11_list(dll, pin)
Return `[(serial_hex, common_name), …]` for the certificates on a token.
```

## Deferred / remote-key signing

```{py:function} atick.prepare_deferred(pdf, style, *, page=1, rect=..., field_name="Atick_1", sub_filter="adbe.pkcs7.detached", ..., contents_size=16384, hash_algo="sha256")
Add an empty signature field + appearance + container; returns `(prepared_pdf, ctx)` where
`ctx["data"]` are the bytes to sign and `ctx["digest"]` their hash.
```

```{py:function} atick.prepare_deferred_multi(pdf, style, placements, *, mode="single", field_name="Atick_1", sub_filter="adbe.pkcs7.detached", ..., certify=0, lock_fields=[])
The multi-placement form (one signature, several pages). Returns `(prepared_pdf, ctx)`.
```

```{py:function} atick.embed(prepared, cms_der)
Embed a detached CMS/PKCS#7 into a prepared PDF. Returns the signed PDF.
```

```{py:function} atick.embed_rawrsa(prepared, raw_sig, signer_cert, *, chain=[], hash_algo="sha256")
Embed a raw RSA signature + signer certificate (e.g. an eSign `rawrsa` reply).
```

```{py:function} atick.cms_pfx(data, pfx, password, *, hash_algo="sha256", pades=False, timestamp=False, tsa_url=None, tsa_auth=None, revocation=False)
A detached CMS over `data` signed with a PFX. `revocation=True` adds the RevocationInfoArchival
attribute (a `pkcs7Pdf`-style reply). Returns the CMS (bytes).
```

```{py:function} atick.sign_hash_pfx(data, pfx, password, *, hash_algo="sha256")
A raw RSA signature over hash(`data`) with a PFX. Returns `(signature, signer_certificate_der)`.
```

## Low-level field API

```{py:function} atick.prepare(pdf, style, *, page=1, rect=..., field_name="Atick_1")
Add ONE empty signature field with an appearance. Returns the PDF.
```

```{py:function} atick.prepare_fields(pdf, styles, placements, names)
Add SEVERAL empty fields at once (a template). Returns the PDF.
```

```{py:function} atick.sign_field(pdf, field_name, *, sub_filter="adbe.pkcs7.detached", ...)
Attach a container to an existing field by name; returns `(prepared_pdf, ctx)`.
```

## Long-term validation & timestamps

```{py:function} atick.add_ltv(pdf, certs, crls=[], ocsps=[])
Add the DSS (validation material) for the given certificates / revocation.
```

```{py:function} atick.add_doctimestamp(pdf, *, tsa_url=None, tsa_auth=None, ltv=True, contents_size=16384)
Append a document timestamp (RFC-3161) over the whole PDF (PAdES-B-LTA).
```

## Documents & utilities

```{py:function} atick.set_metadata(pdf, *, title=None, author=None, subject=None, keywords=None, application=None, created=None, modified=None)
Set the `/Info` metadata on an unsigned PDF.
```

```{py:function} atick.decrypt(pdf, password)
Decrypt a password-protected PDF; returns the plaintext PDF.
```

```{py:function} atick.set_fast_signing(on=True)
Enable/disable the in-memory revocation cache (default on). Disabling also clears it.
```

```{py:function} atick.clear_revocation_cache()
Forget all cached revocation.
```

## Appearance

```{py:class} atick.Style(cn="", org="", ou="", location=None, reason=None, text=None, date=None, heading="Digitally Signed by:", *, show_mark=True, dn=None, image=None, image_rect=None, body=None, green_tick=None, always_check=False, mark_color="#FFFF66", mark_gradient=None, font_size=None, text_color=(0,0,0), bg_color=None, border=False, ..., width=200, height=100)
The verified-signature appearance. `image="cn"` draws the CN on the left; `body=` is a custom-text-
only appearance (`\n` = line, `*x*` = bold); `green_tick=True` is the "?" mark, `always_check=True`
the embedded green tick.
```

```{py:class} atick.Certify
Certification levels: `NONE` (0), `NO_CHANGES` (1), `FORM_FILLING` (2), `FORM_FILLING_ANNOTATIONS` (3).
```

## Exceptions

```{py:exception} atick.AtickError
Raised for every failure (bad password, malformed PDF, network error, …).
```
