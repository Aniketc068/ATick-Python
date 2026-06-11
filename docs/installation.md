# Installation

```bash
pip install atick
```

That is all — ATick has **no other dependencies**. The cryptography, PFX/PKCS#12 parsing, PKCS#11
token access, image decoding, RFC-3161 timestamping and LTV are all built into the package.

- **Python**: 3.8 or newer.
- **Platforms**: Windows, macOS, Linux. Windows-store signing (`sign_winstore`) is Windows-only;
  everything else is cross-platform.
- **Optional**: the Indian-eSign examples sign the request XML with the separate
  [`managex-xml-sdk`](https://pypi.org/project/managex-xml-sdk/) package (`pip install managex-xml-sdk`).

## Verify

```python
import atick
print(atick.__version__)
```

```bash
atick version
```
