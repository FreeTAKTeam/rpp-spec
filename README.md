# Reticulum Package Protocol (RPP)

**RPP 0.3 RC1** defines an M2 ontology on top of RDO.

RPP defines the semantic model for published Packages, Files, Manifests, content Properties and package Relationships using the [RDO distributed M3](https://github.com/FreeTAKTeam/ReticulumDistributedObject).

- **Semantic control plane:** Each Package, File, Manifest, Property and Relationship instance is a separately addressable RDO object with a Reticulum Destination and one owning twin.
- **Binary transfer.** Each signed manifest lists every chunk. The receiver caches the verified manifest and requests missing indexes or ranges by manifest hash. Reticulum Resources carry the manifest on request and the accepted chunk bundles.
- **Content identity:** SHA-256 manifests/chunks identify immutable bytes, not the RDO Destination of the File or Package object.
- **Operations:** Offers, requests, negotiation and receipts are RPP-domain operations over RDO/RNS; transport chunks and session metadata need no independent object Destination.

Read the [normative specification](SPECIFICATION.md) and the [RPP M2 Turtle vocabulary](ontology/rpp.ttl).

The [direct LXMF comparison and 100-chunk example](SPECIFICATION.md#appendix-a-direct-lxmf-delivery-and-rpp-informative) illustrate the airtime cost of a resumed transfer.

RPP depends on RDO's identity, ontology and owner-operation rules. RDO does **not** depend on RPP; neither requires LXMF messaging.

Implementers should start with the [RC1 wire profile and Fabric acceptance gates](profiles/0.3-rc1.md) and the [machine-readable conformance vectors](vectors/rc1.json). End-to-end qualification requires a live Python/Rust RDO owner lookup and bounded RNS Resource transfer.

## Verify the release vectors

The specification tag is `v0.3.0-rc.1`. The wire version is integer `3` on the Link request path `/rpp/3`. From the root of the tagged source or extracted release bundle, run:

```sh
uv run conformance/verify.py
cargo run --locked --manifest-path conformance/rust/Cargo.toml
```

Both consumers encode the diagnostic values in `vectors/rc1.json` and recompute package and signed-manifest digests. Python also checks file and chunk integrity, all rejection cases, and the resume scenario. Rust independently regenerates the Ed25519 manifest signatures. The inputs are public test keys and local bytes. Network interoperability has separate [RDO and RNS acceptance gates](profiles/0.3-rc1.md#fabric-and-downstream-acceptance).

See [proposals/](proposals/) for the proposal process.
