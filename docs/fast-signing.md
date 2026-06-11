# Fast signing

Fast signing is **ON by default**. When LTV is enabled, the first signature fetches the
certificate's CRL/OCSP over the network; ATick then keeps that revocation in an in-memory cache, so
every later signature **with the same certificate** reuses it instead of fetching again. This is a
large speed-up for batch and multi-signature runs (≈ 6× in practice).

```python
atick.set_fast_signing(True)       # default — reuse cached revocation for the same certificate
atick.set_fast_signing(False)      # always fetch fresh (also clears the cache)
atick.clear_revocation_cache()     # forget cached revocation (e.g. after switching certificate)
```

```bash
atick sign in.pdf out.pdf --pfx my.pfx --password ••• --ltv --no-fast   # disable for one run
```

## Notes

- The cache lives in **process memory** only and is gone when the process ends.
- It is keyed per request, so a **different / removed certificate** simply misses and is fetched
  fresh — there is no risk of reusing the wrong certificate's revocation.
- **Timestamps are never cached** — each signature must carry its own unique RFC-3161 token, so the
  timestamp authority is always contacted per signature.
