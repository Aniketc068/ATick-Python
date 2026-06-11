# Quick start

## Sign a PDF with a `.pfx`

```python
import atick

pdf = open("document.pdf", "rb").read()
pfx = open("my_certificate.pfx", "rb").read()

signed = atick.sign_pfx(
    pdf, pfx=pfx, password="••••",
    style=atick.Style(cn="Aniket Chaturvedi", org="Acme Corp", reason="Approved"),
    placements=[(1, (300, 55, 575, 175))],   # page 1, rectangle (x1, y1, x2, y2)
)
open("signed.pdf", "wb").write(signed)
```

`placements` is a list of `(page_number, (x1, y1, x2, y2))` — the signature appearance is drawn in
each rectangle. Page numbers start at 1; coordinates are PDF points from the bottom-left.

## Add a timestamp and long-term validation (PAdES-B-LT)

```python
signed = atick.sign_pfx(
    pdf, pfx=pfx, password="••••",
    style=atick.Style(cn="Aniket Chaturvedi", reason="Approved"),
    placements=[(1, (300, 55, 575, 175))],
    pades=True, timestamp=True, ltv=True,
)
```

See [PAdES levels](pades.md) for B-B / B-T / B-LT / B-LTA.

## The same from the command line

```bash
atick sign document.pdf signed.pdf --pfx my_certificate.pfx --password ••• \
      --cn "Aniket Chaturvedi" --reason Approved --timestamp --ltv \
      --page 1 --rect 300,55,575,175
```

## Error handling

Every failure — wrong password, malformed PDF, unreachable timestamp authority — is a Python
`atick.AtickError`:

```python
try:
    signed = atick.sign_pfx(pdf, pfx=pfx, password="wrong", style=…, placements=…)
except atick.AtickError as e:
    print("signing failed:", e)
```
