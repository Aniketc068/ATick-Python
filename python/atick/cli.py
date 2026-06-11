#!/usr/bin/env python3
"""ATick command-line interface — every signing feature from the terminal.

    atick sign in.pdf out.pdf --pfx cert.pfx --password PW [options]
    atick sign-token in.pdf out.pdf --dll lib.dll --pin PIN --serial HEX [options]
    atick sign-winstore in.pdf out.pdf [--thumbprint HEX] [options]
    atick list-token --dll lib.dll --pin PIN
    atick metadata in.pdf out.pdf --title T --author A ...
    atick decrypt in.pdf out.pdf --password PW
    atick version

Run `atick <command> -h` for the full option list of any command.
"""
import argparse
import sys

from . import (
    Style, Certify, AtickError, __version__, __producer__,
    sign_pfx, sign_pkcs11, sign_winstore, pkcs11_list, set_metadata, decrypt as _decrypt,
    prepare_deferred_multi, embed as _embed, embed_rawrsa as _embed_rawrsa,
    add_doctimestamp as _add_doctimestamp, set_fast_signing as _set_fast_signing,
)

_CERTIFY = {"none": Certify.NONE, "no-changes": Certify.NO_CHANGES,
            "form-fill": Certify.FORM_FILLING, "form-annots": Certify.FORM_FILLING_ANNOTATIONS}


def _placements(a):
    """[] when --invisible, else the --placement list, else a single --page/--rect."""
    if getattr(a, "invisible", False):
        return []
    out = []
    for p in (a.placement or []):
        page, rect = p.split(":")
        out.append((int(page), tuple(int(v) for v in rect.split(","))))
    if not out:
        out = [(a.page, tuple(int(v) for v in a.rect.split(",")))]
    return out


def _style(a):
    kw = {}
    for k in ("cn", "org", "ou", "location", "reason", "text"):
        v = getattr(a, k, None)
        if v:
            kw[k] = v
    if getattr(a, "date", None) is not None:
        kw["date"] = a.date
    if getattr(a, "date_format", None):
        kw["date_format"] = a.date_format
    if getattr(a, "cn_left", False):
        kw["image"] = "cn"
    elif getattr(a, "no_logo", False):
        kw["image"] = False
    elif getattr(a, "image", None):
        kw["image"] = a.image
    if getattr(a, "dn", None):
        kw["dn"] = a.dn
    if getattr(a, "body", None):
        kw["body"] = a.body.replace("\\n", "\n")        # allow a literal \n on the command line
    if getattr(a, "always_check", False):
        kw["always_check"] = True
    elif getattr(a, "no_mark", False):
        kw["green_tick"] = False
    elif getattr(a, "green_tick", False):
        kw["green_tick"] = True
    if getattr(a, "mark_color", None):
        kw["mark_color"] = a.mark_color
    return Style(**kw)


def _appearance_opts(p):
    g = p.add_argument_group("appearance")
    g.add_argument("--cn", help="signer common name (bold line)")
    g.add_argument("--org"); g.add_argument("--ou")
    g.add_argument("--location"); g.add_argument("--reason"); g.add_argument("--text")
    g.add_argument("--image", metavar="PNG", help="your own logo (default = ATick logo)")
    g.add_argument("--no-logo", action="store_true", help="no logo")
    g.add_argument("--cn-left", action="store_true", help="draw the CN as text on the LEFT (Adobe-style) instead of a logo")
    g.add_argument("--dn", help="distinguished name, shown under the 'Signed by:' line")
    g.add_argument("--body", help="custom-text-ONLY appearance (no Signed-by/date); '\\n' = new line, '*x*' = bold")
    g.add_argument("--date", help="signing date text (default: now); '' for no date line")
    g.add_argument("--date-format", help="strftime pattern for the auto date, e.g. %%Y-%%m-%%d %%H:%%M:%%S")
    g.add_argument("--mark-color", help="'?' / tick colour (hex/name/r,g,b)")
    mk = g.add_mutually_exclusive_group()
    mk.add_argument("--green-tick", action="store_true", help="the '?' mark (Adobe greens it if valid+trusted)")
    mk.add_argument("--always-check", action="store_true", help="always-green-tick base (Adobe still reds an invalid sig)")
    mk.add_argument("--no-mark", action="store_true", help="no mark at all (basic signature)")
    pl = p.add_argument_group("placement")
    pl.add_argument("--placement", action="append", metavar="PAGE:X1,Y1,X2,Y2", help="repeatable")
    pl.add_argument("--page", type=int, default=1)
    pl.add_argument("--rect", default="300,55,575,175", metavar="X1,Y1,X2,Y2")
    pl.add_argument("--invisible", action="store_true", help="invisible signature (nothing drawn)")
    pl.add_argument("--mode", default="single", choices=["single", "shared"])
    pl.add_argument("--field-name", default="Atick_1",
                    help="signature field name (auto-uniquified: Atick_1, Atick_2, ... on re-sign)")


def _signing_opts(p):
    g = p.add_argument_group("signature")
    g.add_argument("--no-pades", action="store_true", help="use adbe.pkcs7.detached instead of PAdES")
    g.add_argument("--hash", default="sha256", choices=["sha256", "sha384", "sha512"])
    g.add_argument("--timestamp", action="store_true")
    g.add_argument("--tsa-url"); g.add_argument("--tsa-user"); g.add_argument("--tsa-pass")
    g.add_argument("--ltv", action="store_true", help="PAdES B-LT")
    g.add_argument("--lta", action="store_true", help="PAdES B-LTA (archive timestamp)")
    g.add_argument("--doc-tsa-url")
    g.add_argument("--certify", choices=list(_CERTIFY), help="certification (DocMDP) level")
    g.add_argument("--lock-fields", nargs="*", metavar="FIELD", help="lock fields after signing ('*' = all)")
    g.add_argument("--verify", action="store_true", help="pre-sign expiry + CRL + OCSP checks")
    g.add_argument("--trusted-root", action="append", metavar="SHA1", help="pin a CA root (repeatable)")
    g.add_argument("--contents-size", type=int, default=0, help="signature container bytes (0 = auto)")
    g.add_argument("--no-fast", action="store_true", help="disable the revocation cache (always fetch fresh)")


def _common_signing_kwargs(a):
    if getattr(a, "no_fast", False):
        _set_fast_signing(False)
    tsa_auth = (a.tsa_user, a.tsa_pass) if getattr(a, "tsa_user", None) else None
    return dict(
        style=_style(a), placements=_placements(a), mode=a.mode, field_name=a.field_name,
        pades=not a.no_pades, ltv=a.ltv, lta=a.lta, doc_tsa_url=a.doc_tsa_url,
        reason=a.reason, location=a.location,
        certify=_CERTIFY.get(a.certify, 0), lock_fields=a.lock_fields or [],
        verify=a.verify, trusted_roots=a.trusted_root or [],
        timestamp=a.timestamp, tsa_url=a.tsa_url, tsa_auth=tsa_auth,
        contents_size=a.contents_size,
    )


def _do_sign(a):
    kw = _common_signing_kwargs(a)
    kw.update(hash_algo=a.hash, open_password=a.open_password,
              encrypt_password=a.encrypt_password, owner_password=a.owner_password)
    signed = sign_pfx(open(a.input, "rb").read(), pfx=open(a.pfx, "rb").read(),
                      password=a.password, **kw)
    open(a.output, "wb").write(signed)
    print(f"signed -> {a.output}  ({len(signed)} bytes)")


def _do_sign_token(a):
    kw = _common_signing_kwargs(a)
    kw.pop("timestamp"); kw.pop("tsa_url"); kw.pop("tsa_auth"); kw.pop("contents_size")
    signed = sign_pkcs11(open(a.input, "rb").read(), dll=a.dll, pin=a.pin, serial=a.serial, **kw)
    open(a.output, "wb").write(signed)
    print(f"signed (token) -> {a.output}  ({len(signed)} bytes)")


def _do_sign_winstore(a):
    if sign_winstore is None:
        sys.exit("sign-winstore is only available on Windows")
    kw = _common_signing_kwargs(a)
    kw.pop("timestamp"); kw.pop("tsa_url"); kw.pop("tsa_auth"); kw.pop("contents_size")
    signed = sign_winstore(open(a.input, "rb").read(), thumbprint=a.thumbprint, **kw)
    open(a.output, "wb").write(signed)
    print(f"signed (Windows store) -> {a.output}  ({len(signed)} bytes)")


def _do_list_token(a):
    for serial, cn in pkcs11_list(a.dll, a.pin):
        print(f"{serial}\t{cn}")


def _do_esign_prepare(a):
    prepared, ctx = prepare_deferred_multi(
        open(a.input, "rb").read(), _style(a), _placements(a), mode=a.mode, field_name=a.field_name,
        sub_filter=("ETSI.CAdES.detached" if a.pades else "adbe.pkcs7.detached"),
        certify=_CERTIFY.get(a.certify, 0), contents_size=a.contents_size, hash_algo=a.hash)
    open(a.prepared, "wb").write(prepared)
    print(f"prepared -> {a.prepared}")
    print(f"InputHash ({a.hash}, hex): {bytes(ctx['digest']).hex()}")
    print("Put this hash in your eSign request XML, sign the request (managex-xml-sdk), POST to the "
          "ESP, then: atick esign-embed <prepared> <response.xml> <out.pdf>")


def _do_esign_embed(a):
    import base64
    import xml.etree.ElementTree as ET
    prepared = open(a.prepared, "rb").read()
    root = ET.fromstring(open(a.response, "rb").read())
    if root.get("status") not in ("1", None):
        sys.exit(f"ESP failure: status={root.get('status')} errMsg={root.get('errMsg')}")

    def _text(tag):
        for el in root.iter():
            if el.tag.split("}")[-1] == tag and (el.text or "").strip():
                return el.text.strip()
        return None

    doc_sig = base64.b64decode(_text("DocSignature"))
    is_cms = doc_sig[:1] == b"\x30" and b"\x2a\x86\x48\x86\xf7\x0d\x01\x07\x02" in doc_sig[:40]
    if is_cms:                                          # pkcs7 / pkcs7Pdf / pkcs7complete
        signed = _embed(prepared, doc_sig)
    else:                                               # rawrsa: + UserX509Certificate
        cert = base64.b64decode(_text("UserX509Certificate"))
        signed = _embed_rawrsa(prepared, doc_sig, cert, chain=[], hash_algo=a.hash)
    open(a.output, "wb").write(signed)
    print(f"embedded -> {a.output}  ({len(signed)} bytes)")


def _do_metadata(a):
    out = set_metadata(open(a.input, "rb").read(), title=a.title, author=a.author,
                       subject=a.subject, keywords=a.keywords, application=a.application,
                       created=a.created, modified=a.modified)
    open(a.output, "wb").write(out)
    print(f"metadata set -> {a.output}")


def _do_decrypt(a):
    out = _decrypt(open(a.input, "rb").read(), a.password)
    open(a.output, "wb").write(out)
    print(f"decrypted -> {a.output}")


def _do_doctimestamp(a):
    tsa_auth = (a.tsa_user, a.tsa_pass) if a.tsa_user else None
    out = _add_doctimestamp(open(a.input, "rb").read(), tsa_url=a.tsa_url, tsa_auth=tsa_auth, ltv=not a.no_ltv)
    open(a.output, "wb").write(out)
    print(f"document timestamp added -> {a.output}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="atick", description="ATick — PDF digital signature CLI")
    ap.add_argument("--version", action="version", version=f"ATick {__version__}  ({__producer__})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sign", help="sign with a .pfx / .p12")
    s.add_argument("input"); s.add_argument("output")
    s.add_argument("--pfx", required=True); s.add_argument("--password", required=True)
    s.add_argument("--open-password", help="password of an encrypted INPUT pdf")
    s.add_argument("--encrypt-password", help="password-protect the OUTPUT pdf")
    s.add_argument("--owner-password")
    _appearance_opts(s); _signing_opts(s); s.set_defaults(func=_do_sign)

    t = sub.add_parser("sign-token", help="sign with a PKCS#11 token / smart card / HSM")
    t.add_argument("input"); t.add_argument("output")
    t.add_argument("--dll", required=True); t.add_argument("--pin", required=True); t.add_argument("--serial", required=True)
    _appearance_opts(t); _signing_opts(t); t.set_defaults(func=_do_sign_token)

    w = sub.add_parser("sign-winstore", help="sign with a certificate from the Windows store")
    w.add_argument("input"); w.add_argument("output"); w.add_argument("--thumbprint")
    _appearance_opts(w); _signing_opts(w); w.set_defaults(func=_do_sign_winstore)

    lt = sub.add_parser("list-token", help="list certificates on a PKCS#11 token")
    lt.add_argument("--dll", required=True); lt.add_argument("--pin", required=True)
    lt.set_defaults(func=_do_list_token)

    ep = sub.add_parser("esign-prepare", help="eSign step 1: prepare a PDF + print the InputHash to sign")
    ep.add_argument("input"); ep.add_argument("prepared")
    ep.add_argument("--pades", action="store_true", help="PAdES (ETSI.CAdES) instead of plain CMS")
    ep.add_argument("--certify", choices=list(_CERTIFY), help="certification (DocMDP) level")
    ep.add_argument("--hash", default="sha256", choices=["sha256", "sha384", "sha512"])
    ep.add_argument("--contents-size", type=int, default=60000)
    _appearance_opts(ep); ep.set_defaults(func=_do_esign_prepare)

    ee = sub.add_parser("esign-embed", help="eSign step 2: embed the ESP response XML into the prepared PDF")
    ee.add_argument("prepared"); ee.add_argument("response"); ee.add_argument("output")
    ee.add_argument("--hash", default="sha256", help="hash for a rawrsa response")
    ee.set_defaults(func=_do_esign_embed)

    m = sub.add_parser("metadata", help="set /Info metadata on an unsigned pdf")
    m.add_argument("input"); m.add_argument("output")
    for k in ("title", "author", "subject", "keywords", "application", "created", "modified"):
        m.add_argument(f"--{k}")
    m.set_defaults(func=_do_metadata)

    d = sub.add_parser("decrypt", help="decrypt a password-protected pdf")
    d.add_argument("input"); d.add_argument("output"); d.add_argument("--password", required=True)
    d.set_defaults(func=_do_decrypt)

    dt = sub.add_parser("doctimestamp", help="add a document timestamp (archive timestamp, B-LTA) to a signed pdf")
    dt.add_argument("input"); dt.add_argument("output")
    dt.add_argument("--tsa-url"); dt.add_argument("--tsa-user"); dt.add_argument("--tsa-pass")
    dt.add_argument("--no-ltv", action="store_true", help="don't add the TSA chain to the DSS")
    dt.set_defaults(func=_do_doctimestamp)

    v = sub.add_parser("version", help="show version")
    v.set_defaults(func=lambda a: print(f"ATick {__version__}  ({__producer__})"))

    a = ap.parse_args(argv)
    try:
        a.func(a)
    except AtickError as e:
        print(f"atick: error: {e}", file=sys.stderr); sys.exit(1)
    except FileNotFoundError as e:
        print(f"atick: file not found: {e.filename}", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
