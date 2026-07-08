# Security Exclusions

The old `computing-environment-old.zip` contained a `.p12` file:

```text
pp-DB53F145C3880598ECCEA719DA5B1EF3.p12
```

This unified package intentionally **does not include** that file.

Reason: `.p12` files can contain private keys/certificates. They should not be stored in a general prompt/config folder, synced broadly, or redistributed inside AI workflow packages unless there is a specific, documented need and secret-handling policy.

If this certificate is still needed, keep it in a secure local/secret store and document only its existence and purpose in a private note, not the file itself.
