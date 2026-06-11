#!/usr/bin/env python3
"""
ATick — ALWAYS green tick.

`always_check=True` embeds a real GREEN TICK (the green_tick.png design — filled green check with a
black outline) in a FLAT appearance. It is shown EXACTLY as embedded; Adobe does not overlay its
own validity graphic. NOTE: because it is embedded, it stays green regardless of the certificate's
validity (it will NOT turn red for an invalid/revoked certificate). For a validity-driven mark
(green ✓ / "?" / red ✗ that Adobe repaints), use green_tick.py (the "?" mark) instead.

    python always_green_tick.py   ->  signed/always_green_tick.pdf
"""
import os
import atick

HERE = os.path.dirname(__file__)
SIGNED = os.path.join(HERE, "signed"); os.makedirs(SIGNED, exist_ok=True)
SAMPLES = os.path.join(HERE, "..", "samples")
PLACEMENTS = [(1, (40, 640, 260, 750)), (2, (330, 380, 560, 490)), (3, (180, 60, 400, 170))]

signed = atick.sign_pfx(
    open(os.path.join(SAMPLES, "blank3.pdf"), "rb").read(),
    pfx=open(os.path.join(SAMPLES, "ABC12.pfx"), "rb").read(), password="ABC12",
    style=atick.Style(cn="DS TEST CERTIFICATE 06", org="Acme Corp", reason="Approved",
                      always_check=True),                      # <-- always green tick
    placements=PLACEMENTS, mode="single", pades=True,
)
out = os.path.join(SIGNED, "always_green_tick.pdf")
open(out, "wb").write(signed)
print(f"always green tick -> {out}")
