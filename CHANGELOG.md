# Changelog

## 0.2 - Draft

- Made RPP an M2 ontology specializing the RDO distributed M3 rather than an independent sibling protocol.
- Added ontology/rpp.ttl with Package, File, Manifest, Contains, Supersedes, ContentHash, MediaType, ByteLength and PackageDigest classes.
- Required separately addressable/owned RDO instances for published Properties and Relationships.
- Distinguished the canonical RDO Destination hash from SHA-256 immutable content/package digests.
- Preserved Reticulum Resources for binary manifests, files and chunks without requiring per-chunk RDO objects.
- Retained explicit destination/recipient authorization, signed manifests, integrity validation, resumable transfers, bounded windows and transfer receipts.
- Resolved the draft package-id hash self-reference: calculate SHA-256 over deterministic CBOR manifest excluding key 2 (package_id) and key 7 (signature); sign the populated manifest excluding key 7.
- Kept control envelopes and transient transfer state outside the mandatory ontology instance set.

This is a draft conceptual and wire-profile revision; interoperability validation remains pending.

## 0.1 - Draft

Initial publication of the independent sibling-protocol design, now superseded by Draft 0.2.
