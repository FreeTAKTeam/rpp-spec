# Changelog

## 0.3 RC1 — design candidate

- Assigned the seven commands, signed publication references, manifest grammar and Resource association in the [RC1 profile](profiles/0.3-rc1.md).
- Added deterministic file, update, bundle, resume and rejection [vectors](vectors/rc1.json) for independent implementations.

## 0.3 - Draft

- Adopted [RPP-0001](proposals/RPP-0001-manifest-reuse.md). Every signed manifest enumerates the index, logical length and SHA-256 digest of every chunk.
- Defined `manifest_hash` over the exact signed manifest bytes. Receivers request a manifest on a cache miss and resume directly from a verified cached copy.
- Required receivers to select missing chunks by index or range and publishers to send only requested chunks in accepted, ordered bundles. Authorization applies on every resumed pull.
- Added an informative direct LXMF comparison and a 100-chunk reconnect example. Draft 0.2 manifests with incomplete inventories require republication for Draft 0.3.

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
