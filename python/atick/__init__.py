"""
ATick — standalone PDF digital-signature library.

ATick signs PDFs end-to-end on its own — no external libraries required. The whole engine
(PAdES/CMS signing, RFC-3161 timestamping, LTV/DSS, and the verified Green-Tick appearance)
ships inside the package itself, so there is nothing else to install.

One-call signing with a .pfx
-----------------------------
    import atick

    signed = atick.sign_pfx(
        open("doc.pdf", "rb").read(),
        pfx=open("cert.pfx", "rb").read(), password="secret",
        style=atick.Style(cn="Aniket Chaturvedi", image="logo.png"),
        placements=[(1, (40, 60, 260, 160))],
        pades=True, hash_algo="sha256",
        timestamp=True,                       # PAdES-B-T (built-in TSA + fallback)
        ltv=True,                             # PAdES-B-LT
        lta=True,                             # PAdES-B-LTA (archive document timestamp)
    )
    open("signed.pdf", "wb").write(signed)

Deferred / external signer (eSign ESP, HSM, smart-card …)
---------------------------------------------------------
When the private key lives elsewhere (an eSign service, an HSM, a token), use the two-step
flow: ``prepare_deferred(...)`` builds the field + appearance + an empty signing container and
returns the bytes-to-sign; the external signer produces a detached CMS; ``embed(...)`` inserts
it — the appearance can never be overwritten.

    prepared, ctx = atick.prepare_deferred(pdf, atick.Style(), field_name="Signature1")
    cms = my_signer(ctx["data"])              # detached PKCS#7/CMS over ctx["data"]
    signed = atick.embed(prepared, cms)

Everything is customizable through ``atick.Style`` (text, font, colors, border, mark position,
logo).
"""

import datetime as _datetime

from ._atick import (
    prepare, prepare_deferred, prepare_deferred_multi, prepare_fields, sign_field,
    sign_pfx, sign_pkcs11, pkcs11_list, embed, embed_rawrsa, add_ltv, add_doctimestamp, mark_png, mark_content,
    default_logo, set_metadata, decrypt, cms_pfx, sign_hash_pfx,
    set_fast_signing, clear_revocation_cache,
    AtickError, build_style as _build_style, __version__, __producer__,
)

class Certify:
    """Certification (DocMDP) levels for the ``certify=`` argument. PDF defines exactly these
    three levels (plus a normal, non-certifying signature):

        Certify.NONE                      0  normal approval signature (no certification)
        Certify.NO_CHANGES                1  document is locked — NO changes allowed at all
        Certify.FORM_FILLING              2  only form filling + further signing allowed
        Certify.FORM_FILLING_ANNOTATIONS  3  form filling + annotations + signing allowed

    Only the FIRST (certifying) signature uses this; later signatures are approval signatures.
    """
    NONE = 0
    NO_CHANGES = 1
    FORM_FILLING = 2
    FORM_FILLING_ANNOTATIONS = 3


try:                       # Windows-only: sign with a certificate from the Windows store
    from ._atick import sign_winstore
except ImportError:
    sign_winstore = None


_NAMED_COLORS = {
    "black": (0, 0, 0), "white": (1, 1, 1), "red": (1, 0, 0), "green": (0, .5, 0),
    "lime": (0, 1, 0), "blue": (0, 0, 1), "yellow": (1, 1, 0), "orange": (1, .647, 0),
    "gold": (1, .843, 0), "gray": (.5, .5, .5), "grey": (.5, .5, .5), "silver": (.75, .75, .75),
    "purple": (.5, 0, .5), "violet": (.933, .51, .933), "indigo": (.294, 0, .51),
    "cyan": (0, 1, 1), "magenta": (1, 0, 1), "pink": (1, .753, .796), "brown": (.647, .165, .165),
    "navy": (0, 0, .5), "teal": (0, .5, .5), "maroon": (.5, 0, 0), "olive": (.5, .5, 0),
    "darkgreen": (0, .392, 0), "skyblue": (.529, .808, .922), "crimson": (.863, .078, .235),
}


def _parse_color(c):
    """Accept any common Python colour: a name ("red"), a hex string ("#FFD700"/"FD0"),
    or an (r, g, b) tuple in 0..1 floats or 0..255 ints. Returns (r, g, b) as 0..1 floats."""
    if isinstance(c, str):
        s = c.strip().lower().lstrip("#")
        if s in _NAMED_COLORS:
            return _NAMED_COLORS[s]
        if len(s) == 3:
            s = "".join(ch * 2 for ch in s)
        if len(s) == 6 and all(ch in "0123456789abcdef" for ch in s):
            return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
        raise ValueError(f"unknown colour: {c!r}")
    if isinstance(c, (tuple, list)) and len(c) == 3:
        if all(isinstance(x, int) for x in c) and any(x > 1 for x in c):
            return tuple(x / 255 for x in c)            # 0..255 ints
        return tuple(float(x) for x in c)               # 0..1 floats
    raise ValueError(f"unknown colour: {c!r}")


def Style(
    cn="", org="", ou="", location=None, reason=None, text=None, date=None,
    heading="Digitally Signed by:", *,
    date_format="%d-%b-%Y %I:%M %p",   # strftime pattern for the auto date (when date=None); any format

    show_mark=True,
    body=None,                   # custom-text-ONLY appearance: just this text (no "Signed by"/date/CN).
                                 # "\n" -> new line; "*word*" -> bold that run. Overrides cn/date/etc.
    dn=None,                     # distinguished name -> shown UNDER the "Signed by:" line (optional)
    image=None,                  # left side: None -> ATick logo; False -> none; path/bytes -> your own;
    image_rect=None,             #            "cn" -> draw the CN as text on the LEFT (Adobe-style).
    font_size=None, top_reserve=0.32, text_dx=None, text_top=None,
    text_color=(0.0, 0.0, 0.0), bg_color=None,
    border=False, border_color=(0.0, 0.0, 0.0), border_width=1.0,
    mark_scale=None, mark_dx=None, mark_dy=None,
    mark_color="#FFFF66",         # the "?" mark colour — any Python colour (hex/name/RGB tuple)
    mark_gradient=None,           # list of 2+ colours -> gradient fill of the "?" (overrides mark_color)
    green_tick=None,              # the "?" mark: True -> embed it (Adobe greens it for trusted certs),
                                  #                False -> embed nothing. (alias of show_mark)
    always_check=False,           # True -> ALWAYS embed a real green tick (✓), instead of the "?"
    width=200, height=100,
):
    """Build the verified-signature appearance. Every line appears only if you provide it:

        Digitally Signed by: <cn>     (the CN is bold)
        <org>
        <ou>
        <blank>
        Location: <location>
        Reason: <reason>
        <custom text>
        Date: <date or sign-time, e.g. 08-Jun-2026 12:37 PM>

    ``date=""`` drops the date line; ``None`` uses the current sign time. The layout, the font
    auto-fit and the image placement are computed inside ATick.

    The left-side logo follows the rule: ``image=None`` (default) uses ATick's built-in logo,
    ``image=False`` shows no logo, and a path or bytes uses your own image.
    """
    if date is None:                       # auto date in the caller's format; "" -> no date line
        date = _datetime.datetime.now().strftime(date_format)

    # left side: None -> ATick default; False -> none; "cn" -> CN text; str path -> file; bytes -> raw.
    left_cn = False
    if image == "cn":
        img_bytes = None
        left_cn = True
    elif image is False:
        img_bytes = None
    elif image is None:
        img_bytes = default_logo()
    elif isinstance(image, str):
        img_bytes = open(image, "rb").read()
    else:
        img_bytes = bytes(image)

    # green_tick is an alias for show_mark: it controls whether the "?" mark is embedded at all
    if green_tick is not None:
        show_mark = bool(green_tick)
    # always_check -> a real, always-shown green tick (needs the mark layer enabled)
    _tick = bool(always_check)
    if _tick:
        show_mark = True
    # the tick uses a green default colour (unless the caller picked their own mark_color)
    _mc = mark_color
    if _tick and mark_color == "#FFFF66":
        _mc = "#1Fa84F"

    return _build_style(
        cn=cn, org=org, ou=ou, location=location, reason=reason, text=text, date=date,
        heading=heading, show_mark=show_mark, top_reserve=top_reserve,
        font_size=font_size, text_dx=text_dx, text_top=text_top,
        text_color=text_color, bg_color=bg_color,
        border=border, border_color=border_color, border_width=border_width,
        mark_scale=mark_scale, mark_dx=mark_dx, mark_dy=mark_dy,
        mark_color=_parse_color(_mc),
        mark_gradient=[_parse_color(c) for c in mark_gradient] if mark_gradient else None,
        green_tick=_tick, dn=dn, left_cn=left_cn, body=body,
        image=img_bytes, image_rect=image_rect,
        width=width, height=height,
    )


def mark_png_file(path=None):
    """Write the mark PNG to ``path`` (or a temp file) and return the path — for code paths whose
    image option wants a filename."""
    import os, tempfile
    if path is None:
        path = os.path.join(tempfile.gettempdir(), "atick_mark.png")
    with open(path, "wb") as f:
        f.write(mark_png())
    return path


__all__ = [
    "Style", "Certify", "sign_pfx", "sign_pkcs11", "pkcs11_list", "sign_winstore",
    "prepare", "prepare_deferred", "prepare_deferred_multi",
    "prepare_fields", "sign_field", "embed", "embed_rawrsa", "set_metadata", "decrypt", "add_ltv", "add_doctimestamp",
    "mark_png", "mark_content", "mark_png_file", "cms_pfx", "sign_hash_pfx",
    "set_fast_signing", "clear_revocation_cache",
    "AtickError", "__version__",
]
