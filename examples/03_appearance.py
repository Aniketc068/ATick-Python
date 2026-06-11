#!/usr/bin/env python3
"""
ATick — Example 03: Customizing the signature appearance with `atick.Style` (multi-page).

Every line appears only if you provide it, in this fixed order:

    Digitally Signed by: <cn>      (the CN is bold)
    <org>
    <ou>
    <blank line>
    Location: <location>
    Reason: <reason>
    <your custom text>             (any extra text, multi-line ok)
    Date: <date>                   (default = sign time, e.g. 09-Jun-2026 01:13 PM)

The LOGO on the left follows: image not given -> ATick's default logo ; image=False -> no logo ;
image="path"/bytes -> your own (transparency kept on any page background). The font auto-fits.

    python 03_appearance.py
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
OUT = os.path.join(SIGNED, "03_appearance.pdf")

style = atick.Style(
    cn="DS TEST CERTIFICATE 06",        # bold name line
    org="Acme Corp CA",                 # organization
    ou="Class 3",                       # organizational unit
    location="New Delhi, India",
    reason="Approved for release",
    text="Verified by ATick",           # any custom text
    # date="09-Jun-2026 12:37 PM",      # omit -> current sign time; date="" -> hide the line
    image=os.path.join(SAMPLES, "sign.png"),   # YOUR OWN logo (omit this line for ATick's default)
    show_mark=True,                     # the "?" / green-tick mark
    # text_color=(0, 0, 0), bg_color=(0.97, 0.97, 1.0),   # colors (optional)
    # border=True, border_color=(0, 0, 0.5), border_width=1.0,   # border (optional)
    width=240, height=120,              # appearance box size (points)
)

# custom coordinates on several pages
PLACEMENTS = [(1, (320, 600, 575, 720)), (2, (40, 360, 295, 480)), (3, (170, 55, 425, 175))]

signed = atick.sign_pfx(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    pfx=open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read(), password="ABC12",
    style=style, placements=PLACEMENTS, mode="single", pades=True,
)
open(OUT, "wb").write(signed)
print(f"signed on {len(PLACEMENTS)} pages -> {OUT}  ({len(signed)} bytes)")
