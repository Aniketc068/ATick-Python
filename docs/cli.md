# Command line

Every feature is available from the terminal as `atick` (or `python -m atick`).

```text
atick sign           sign with a .pfx / .p12
atick sign-token     sign with a PKCS#11 token / smart-card / HSM
atick sign-winstore  sign with a certificate from the Windows store
atick list-token     list certificates on a PKCS#11 token
atick esign-prepare  eSign step 1: prepare a PDF + print the InputHash
atick esign-embed    eSign step 2: embed the ESP response XML
atick doctimestamp   add a document timestamp (B-LTA) to a signed PDF
atick metadata       set /Info metadata on an unsigned PDF
atick decrypt        decrypt a password-protected PDF
atick version        show the version
```

Run `atick <command> -h` for every option.

## `atick sign`

```bash
atick sign in.pdf out.pdf --pfx my.pfx --password ••• \
      --cn "Aniket Chaturvedi" --org "Acme Corp" --reason Approved \
      --timestamp --ltv \
      --page 1 --rect 300,55,575,175
```

Key options:

| Option | Meaning |
|---|---|
| `--pfx`, `--password` | the signing certificate |
| `--timestamp`, `--tsa-url`, `--tsa-user`, `--tsa-pass` | RFC-3161 timestamp |
| `--ltv`, `--lta` | long-term validation / document timestamp |
| `--no-pades` | plain CMS instead of PAdES |
| `--hash sha256\|sha384\|sha512` | digest algorithm |
| `--certify none\|no-changes\|form-fill\|form-annots` | certification level |
| `--lock-fields F1 F2 …` | lock fields (`*` = all) |
| `--verify`, `--trusted-root SHA1` | pre-sign checks |
| `--encrypt-password`, `--owner-password`, `--open-password` | encryption |
| `--no-fast` | disable the revocation cache |
| **Appearance** | `--cn`, `--org`, `--reason`, `--location`, `--image PNG`, `--no-logo`, `--cn-left`, `--dn`, `--body`, `--mark-color`, `--green-tick`, `--always-check`, `--no-mark` |
| **Placement** | `--placement PAGE:X1,Y1,X2,Y2` (repeatable), `--page`, `--rect`, `--invisible`, `--mode`, `--field-name` |

## Examples

```bash
# CN on the left + distinguished name, always-green tick
atick sign in.pdf out.pdf --pfx my.pfx --password ••• --cn "Aniket Chaturvedi" \
      --cn-left --dn "CN=Aniket, O=Personal, C=IN" --always-check

# custom-text-only appearance (\n = new line, *x* = bold)
atick sign in.pdf out.pdf --pfx my.pfx --password ••• --body "*APPROVED*\nby *Aniket*"

# sign an already-signed PDF (incremental — existing signatures stay valid)
atick sign signed.pdf signed2.pdf --pfx my.pfx --password ••• --timestamp --ltv
```
