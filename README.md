# Reticulum Package Protocol (RPP)

**RPP Draft 0.3** defines an M2 ontology on top of RDO.

RPP defines the semantic model for published Packages, Files, Manifests, content Properties and package Relationships using the [RDO distributed M3](https://github.com/FreeTAKTeam/ReticulumDistributedObject).

- **Semantic control plane:** Each Package, File, Manifest, Property and Relationship instance is a separately addressable RDO object with a Reticulum Destination and one owning twin.
- **Binary transfer.** Each signed manifest lists every chunk. The receiver caches the verified manifest and requests missing indexes or ranges by manifest hash. Reticulum Resources carry the manifest on request and the accepted chunk bundles.
- **Content identity:** SHA-256 manifests/chunks identify immutable bytes, not the RDO Destination of the File or Package object.
- **Operations:** Offers, requests, negotiation and receipts are RPP-domain operations over RDO/RNS; transport chunks and session metadata need no independent object Destination.

Read the [normative specification](SPECIFICATION.md) and the [RPP M2 Turtle vocabulary](ontology/rpp.ttl).

The [direct LXMF comparison and 100-chunk example](SPECIFICATION.md#appendix-a-direct-lxmf-delivery-and-rpp-informative) illustrate the airtime cost of a resumed transfer.

RPP depends on RDO's identity, ontology and owner-operation rules. RDO does **not** depend on RPP; neither requires LXMF messaging.

This repository contains draft specifications and a vocabulary, not a production implementation. End-to-end interoperability still requires a tested RDO address binding and RPP compact wire profile. The prior Draft 0.1 sibling-protocol model is superseded.

See [proposals/](proposals/) for the proposal process.
