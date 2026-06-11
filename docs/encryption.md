# Encryption & metadata

## Password-protect the output

```python
signed = atick.sign_pfx(
    pdf, pfx=…, password="••••", style=…, placements=…,
    encrypt_password="open-pw",      # user password (to open the PDF)
    owner_password="owner-pw",       # optional owner password (defaults to the user password)
)
```

The output is AES-128 encrypted; the signature stays valid (the `/Contents` is exempt from
encryption, so the byte range still verifies).

## Sign an encrypted input

```python
signed = atick.sign_pfx(pdf, pfx=…, password="••••", style=…, placements=…,
                        open_password="the-input-password")
```

## Decrypt a PDF

```python
plain = atick.decrypt(encrypted_pdf, "the-password")
```

## Set document metadata

```python
out = atick.set_metadata(
    pdf,
    title="Agreement",
    author="Aniket Chaturvedi",
    subject="Service contract",
    keywords="contract, signed",
    application="My App",
    created="D:20260610120000+05'30'",
    modified="D:20260610120000+05'30'",
)
```

Set metadata on an unsigned PDF before signing (changing metadata after signing would invalidate
the signature).
