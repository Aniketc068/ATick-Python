---
sd_hide_title: true
---

# ATick

```{raw} html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "ATick",
  "alternateName": "ATick PDF digital signature library",
  "description": "Standalone Python library for PDF digital signatures — PAdES and CMS signing with a PFX/PEM file, USB tokens (PKCS#11), the Windows certificate store and Indian eSign (CCA); RFC-3161 timestamps, long-term validation (LTV), and a green-tick verified-signature appearance that Adobe shows as valid. Zero dependencies.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Windows, Linux, macOS",
  "programmingLanguage": "Python",
  "softwareVersion": "1.0.2",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "license": "https://www.gnu.org/licenses/agpl-3.0.html",
  "author": { "@type": "Person", "name": "Aniket Chaturvedi" },
  "url": "https://atick.readthedocs.io/",
  "codeRepository": "https://github.com/Aniketc068/ATick",
  "downloadUrl": "https://pypi.org/project/atick/",
  "keywords": "PDF digital signature, sign PDF Python, PAdES, CAdES, eSign, PKCS#11, LTV, RFC-3161 timestamp, Adobe valid signature, green tick"
}
</script>
```

```{image} _static/green_tick.png
:class: hero-mark
:width: 78px
:align: center
```

```{rst-class} hero-title
Sign PDFs with confidence
```

```{rst-class} hero-sub
ATick is the standalone PDF digital-signature library for Python — PAdES & CMS signing, USB tokens,
the Windows store and Indian eSign, with **zero dependencies**.
```

::::{div} hero-buttons
:::{button-ref} quickstart
:color: primary
:class: hero-btn
Get started  →
:::
:::{button-ref} api
:color: primary
:outline:
:class: hero-btn
API reference
:::
::::

```python
import atick

signed = atick.sign_pfx(
    open("doc.pdf", "rb").read(),
    pfx=open("my.pfx", "rb").read(), password="••••",
    style=atick.Style(cn="Aniket Chaturvedi", reason="Approved"),
    placements=[(1, (300, 55, 575, 175))],
    pades=True, timestamp=True, ltv=True,     # PAdES-B-LT
)
open("signed.pdf", "wb").write(signed)
```

---

## Everything you need to sign PDFs

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`key;1.3em;sd-text-success` Sign anywhere
PFX/P12 **or PEM** files, USB tokens / smart-cards / HSMs (PKCS#11), and the Windows certificate
store — one consistent API.
+++
[Signing methods »](signing.md)
:::

:::{grid-item-card} {octicon}`shield-check;1.3em;sd-text-success` Full PAdES
B-B, B-T, **B-LT**, **B-LTA** with RFC-3161 timestamps and long-term validation — recognised by
Adobe Acrobat as *“PAdES Signature Level”*.
+++
[PAdES levels »](pades.md)
:::

:::{grid-item-card} {octicon}`globe;1.3em;sd-text-success` Indian eSign
The complete CCA eSign flow (every API version) — prepare, sign the request, embed the ESP reply
(rawrsa / PKCS7 / pkcs7Pdf / pkcs7complete).
+++
[eSign guide »](esign.md)
:::

:::{grid-item-card} {octicon}`paintbrush;1.3em;sd-text-success` Rich appearance
Logo or CN-on-the-left, the validity mark (`?` / green tick), distinguished name, custom text,
invisible signatures, any date format.
+++
[Appearance »](appearance.md)
:::

:::{grid-item-card} {octicon}`lock;1.3em;sd-text-success` Trust & control
Certification (DocMDP), field-locking (FieldMDP), pre-sign expiry / CRL / OCSP checks, password
protection and metadata.
+++
[Certification »](certification.md)
:::

:::{grid-item-card} {octicon}`rocket;1.3em;sd-text-success` Built for scale
A revocation cache makes batch signing ~6× faster, multi-signatory documents stay valid, and every
error is a clean Python exception.
+++
[Fast signing »](fast-signing.md)
:::

::::

---

## The green tick your readers trust

ATick draws a verified-signature appearance with a green tick. When the certificate is valid and
trusted, Adobe Reader / Acrobat shows **“Signed and all signatures are valid.”** — the reassurance
every signed document needs.

```{image} _static/valid_signature_adobe.png
:alt: Adobe Reader — signed and all signatures are valid, with the ATick green tick
:width: 600px
:align: center
:class: shadow-img
```

---

## Why ATick

```{list-table}
:header-rows: 1
:widths: 32 68

* - 
  - ATick
* - **Dependencies**
  - none — the crypto, PKCS#12/PEM, PKCS#11, image decode, timestamping and LTV are all built in
* - **Install**
  - `pip install atick` — one self-contained package
* - **Interfaces**
  - a Python API *and* a full `atick` command-line tool
* - **Platforms**
  - Windows, Linux and macOS (the Windows-store picker is Windows-only)
* - **Errors**
  - every failure is a Python `atick.AtickError` you can catch
```

```{toctree}
:hidden:

getting-started
guide
reference
```
