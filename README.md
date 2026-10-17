# Reticulum Package Protocol (RPP)

**Status: Draft 0.2 — M2 ontology on top of RDO.**

RPP defines the semantic model for published Packages, Files, Manifests, content Properties and package Relationships using the [RDO distributed M3](https://github.com/FreeTAKTeam/ReticulumDistributedObject).

- **Semantic control plane:** Each Package, File, Manifest, Property and Relationship instance is a separately addressable RDO object with a Reticulum Destination and one owning twin.
- **Binary data plane:** Signed manifests, file bytes and chunk bundles transfer using Reticulum Resources, with bounded transfers, verification and resumption.
- **Content identity:** SHA-256 manifests/chunks identify immutable bytes, not the RDO Destination of the File or Package object.
- **Operations:** Offers, requests, negotiation and receipts are RPP-domain operations over RDO/RNS; transport chunks and session metadata need no independent object Destination.

Read the [normative specification](SPECIFICATION.md) and the [RPP M2 Turtle vocabulary](ontology/rpp.ttl).

RPP depends on RDO's identity, ontology and owner-operation rules. RDO does **not** depend on RPP; neither requires LXMF messaging.

This repository contains draft specifications and a vocabulary, not a production implementation. End-to-end interoperability still requires a tested RDO address binding and RPP compact wire profile. The prior Draft 0.1 sibling-protocol model is superseded.

See [proposals/](proposals/) for the proposal process.
