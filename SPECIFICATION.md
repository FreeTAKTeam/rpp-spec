# Reticulum Package Protocol (RPP)

Protocol: Reticulum Package Protocol
Acronym: RPP
Status: Draft
Version: 0.1
Transport: Reticulum Network Stack

## 1. Status of This Document

This document is the normative Draft 0.1 specification for the Reticulum Package Protocol (RPP).

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

Text marked as **Non-normative** explains intent or gives implementation guidance. It does not add protocol requirements.

**Publication note (non-normative):** Earlier working material used the label “v0.2-draft”. This repository publishes the requested Draft 0.1 specification and does not claim that an earlier working draft was a released protocol version.

## 2. Purpose and Scope

RPP defines generic package and resource distribution using Reticulum Network Stack primitives.

RPP is intended for efficient sharing of packages, files, datasets, snapshots, repositories, binaries, and other bulk resources over constrained, intermittent, delayed, or loss-prone Reticulum links.

RPP defines package identity, manifests, destination-scoped sharing, authorization, integrity, versioned immutable packages, resource planning, resumable transfer, and delivery status.

RPP does not define the meaning of the package contents. A package MAY contain content for any application, but RPP semantics MUST remain application-independent and mission-independent.

RPP is a package and resource protocol. It MUST NOT be used to represent semantic relationships between entities; those semantics belong to a separate protocol such as RDO.

## 3. Design Goals and Non-Goals

### 3.1 Design goals

RPP has the following goals:

1. Use Reticulum Network Stack primitives directly.
2. Keep control overhead small through CBOR where this specification defines CBOR structures.
3. Share packages privately with explicitly selected destinations.
4. Avoid public package inventories and announce-based package discovery.
5. Use content-derived identity and end-to-end integrity verification.
6. Support large packages over constrained Reticulum links.
7. Support resumable, bounded, and adaptive resource transfer.
8. Preserve package versioning and provenance without requiring a central server.
9. Permit disconnected operation, caching, replication, and later retrieval.
10. Remain independently usable from RDO, LXMF, and application runtimes.

### 3.2 Non-goals

RPP does not define:

- a mission model, operational vocabulary, or application semantics;
- a distributed object or semantic relationship model;
- a Git protocol, Git reference negotiation protocol, or Git merge model;
- a messaging or mailbox protocol;
- a particular database, filesystem, programming language, or implementation;
- a required global package catalog;
- package discovery through public Reticulum announces;
- a mandatory storage, cache, compression, or scheduling implementation;
- a requirement that every recipient receive every package resource.

## 4. Terminology

**Package**: An immutable, identified collection of one or more resources and a signed manifest.

**Resource**: A transferable logical content unit within a package. A resource MAY be a file, a group of chunks, a manifest, or another declared content unit.

**Manifest**: The metadata structure that describes a package, its resources, content hashes, version information, authorization-related information, and optional extensions.

**Chunk**: A content-addressed portion of a resource.

**Bundle**: A transfer grouping of one or more chunks or resource descriptors selected for one RNS Resource transfer.

**Publisher**: The party that signs or offers a package.

**Recipient**: A destination explicitly authorized to receive or request a package or resource.

**Offer**: An addressed proposal to make a package available to a selected recipient.

**Capability token**: A recipient-scoped authorization value that permits a defined package or resource action.

**Package identifier**: The content-derived identity of a package.

**Manifest hash**: The digest of the canonical manifest used to identify and verify the package manifest.

**Transfer session**: The state associated with a package transfer between a publisher and recipient.

**RNS Resource**: The Reticulum Network Stack bulk-transfer primitive. It is distinct from the RPP logical Resource.

**Explicit destination**: A Reticulum destination selected by the publisher or otherwise authorized by a package policy. It is not a public package inventory.

## 5. Protocol Layering and Independence

### 5.1 RNS foundation

RPP uses RNS primitives directly:

- **RNS Identity** provides the cryptographic identity used by a participant and its signatures.
- **RNS Destination** identifies an addressed endpoint.
- **RNS Link** provides a session for control exchange and negotiation.
- **RNS Packet** carries small control messages.
- **RNS Resource** carries manifests and bulk resource data.
- **RNS PacketReceipt** MAY be used where a delivery receipt is useful.

RPP MUST NOT require another application protocol to define the meaning of these operations.

### 5.2 Relationship to RDO

RDO and RPP are sibling protocols:

```text
Reticulum Network Stack
│
├── RDO
│   └── Distributed object semantics
│
└── RPP
    └── Package/resource distribution
```

RPP MUST NOT depend on RDO. RDO MUST NOT require RPP.

An RDO object MAY reference an RPP package, snapshot, attachment, repository, or other external resource. An RPP package MAY contain serialized RDO information, but RPP does not acquire RDO semantic requirements by doing so.

### 5.3 Relationship to LXMF

RPP does not depend on LXMF and MUST NOT require LXMF message semantics.

An implementation MAY reuse RNS functionality from a library or project that also implements LXMF. Such reuse is an implementation choice and does not make LXMF part of the RPP protocol.

LXMF MAY carry a reference to an RPP package when a separate integration chooses to do so, but LXMF is not required for RPP control or transfer.

## 6. Package and Resource Model

### 6.1 Immutable packages

A package is immutable after publication. A publisher MUST NOT modify package content while retaining the same package identifier.

A correction, update, or replacement MUST be represented as a new package with a new content-derived identifier. The new manifest MAY refer to previous package identifiers and MAY carry a sequence value.

A recipient MAY retain multiple package versions. Retention, garbage collection, and local storage policy are outside this specification.

### 6.2 Package identity

The package identifier MUST be derived from the SHA-256 digest of the canonical, signature-free manifest according to the RPP manifest canonicalization rules.

The manifest hash MUST be verifiable independently of the transport session.

The working material available for this Draft 0.1 publication does not define whether the `package_id` field itself is omitted from the hash input or represented by a special value. This self-reference treatment is therefore intentionally unresolved and MUST be fixed by a future normative proposal before implementations claim wire-level interoperability for package identifiers.

A receiver MUST verify the package identifier and manifest hash before treating a package as accepted metadata.

The package identifier MUST NOT be derived from a local filename, local database key, transport path, or publisher-local storage location.

### 6.3 Resource identity

A chunk identifier MUST be the SHA-256 digest of the chunk bytes.

A resource descriptor SHOULD include a resource identifier, resource kind, logical size, content hash, and any bundle or chunk descriptors needed to request or verify the resource.

A file descriptor SHOULD include its path or logical name, logical size, content hash, media type when known, file range when applicable, and the range of chunks that carries its content.

The logical content hash and logical size MUST describe the uncompressed logical content. If a transfer encoding compresses content, the manifest MUST identify that encoding and verification MUST still validate the logical content.

### 6.4 References and package contents

A package MAY contain arbitrary opaque content, file sets, serialized records, snapshots, or repository artifacts.

RPP MUST NOT assign mission-specific meaning to paths, media types, application profiles, or application metadata.

Applications MAY define profiles for package content. Such profiles MUST remain outside the RPP core semantics and MUST be identified by an extension or profile identifier.

## 7. Encoding

### 7.1 CBOR control structures

Where RPP defines a control or manifest structure, it uses CBOR.

RPP control maps and signed or hashed metadata MUST use deterministic CBOR. Integer map keys SHOULD be used for defined core fields to reduce overhead on constrained links.

A sender MUST NOT sign or hash one CBOR representation and transfer a semantically different representation under the same identifier.

A receiver MUST reject malformed CBOR, unknown critical extensions, and data that cannot be decoded according to the applicable RPP version.

### 7.2 Canonicalization

The canonicalization procedure MUST be applied consistently before calculating a manifest hash or signature.

The signature field MUST be excluded from the signature input.

The package identity calculation MUST be non-circular and MUST produce the same digest for the same logical manifest under all conforming implementations.

Implementations MUST NOT use map insertion order, local formatting, filesystem ordering, or language-specific object serialization as a substitute for deterministic CBOR.

### 7.3 Content encoding

Package content bytes are opaque to RPP unless the manifest declares a content or compression profile.

A sender MAY compress content when the declared transfer representation is smaller or otherwise more efficient. The compressed representation MUST be identified, and the receiver MUST verify the logical uncompressed content against the manifest.

A receiver MUST NOT silently interpret an unknown compression, encryption, or content profile.

## 8. Cryptographic Profile

### 8.1 Required algorithms

The RPP Draft 0.1 cryptographic profile uses:

- SHA-256 for package, manifest, resource, file, and chunk digests where a digest is required;
- Ed25519 for publisher and authorization signatures where a signature is required;
- deterministic CBOR as the input representation for signed or hashed RPP metadata.

An implementation claiming core RPP conformance MUST support verification of these algorithms.

### 8.2 Manifest signatures

A publisher signature MUST cover the canonical manifest with the signature field removed.

The signature MUST be associated with the publisher identity or destination needed to verify it.

A recipient MUST verify the signature before accepting a manifest as authentic publisher metadata.

A recipient MUST reject or quarantine a manifest with an invalid signature, an unavailable required signer, an unauthorized signer, or a signer that is outside the applicable package policy.

### 8.3 Chunk and resource verification

A recipient MUST verify each received chunk against its declared chunk identifier or hash.

A recipient MUST verify resource and file digests before reporting a complete verified transfer.

A recipient MUST NOT report a package as complete and verified when required chunks, resources, or manifest checks remain unresolved.

## 9. Package Manifest

### 9.1 Core manifest content

A manifest MUST identify the package, publisher, content size, content type, resources or files, and integrity information needed to retrieve and verify the package.

A conforming publisher MUST sign the manifest using the cryptographic profile in Section 8. A recipient MUST verify that signature before accepting the manifest as authoritative package metadata.

The following fields are defined by the RPP manifest model. Integer keys shown below are the compact CBOR key assignments from the working RPP design; optional fields MAY be omitted.

| Key | Field | Requirement |
|---:|---|---|
| 0 | manifest type | MUST identify an RPP manifest |
| 1 | manifest/schema version | MUST identify the manifest schema |
| 2 | package_id | MUST identify the package |
| 4 | publisher_destination | MUST identify the publisher destination or signing identity |
| 6 | created_timestamp | MAY identify creation time |
| 7 | signature | MUST carry the publisher signature when the manifest is signed |
| 10 | extensions | MAY carry understood non-critical extensions |
| 11 | critical_extensions | MAY identify extensions that MUST be understood |
| 12 | package_expiry | MAY identify an expiry time |
| 14 | previous_package_ids | MAY identify superseded or related packages |
| 15 | sequence | MAY identify a publisher sequence |
| 20 | total_uncompressed_size | MUST identify logical uncompressed size |
| 24 | chunk_count | MUST identify the declared chunk count when chunks are used |
| 25 | package_content_type | MAY identify a content profile |
| 26 | compression_algorithm | MAY identify compression |
| 27 | encryption_profile | MAY identify an encryption profile |
| 28 | ledger_hash | MAY identify an external package ledger |
| 29 | revocation_hash | MAY identify revocation information |
| 31 | files | MAY describe files or logical members |
| 32 | chunks | MUST describe chunks when direct chunk descriptors are used |
| 33 | package_name | MAY provide a display name |
| 34 | package_version | MAY provide an application or content version |
| 35 | application_profile | MAY identify an external application profile |
| 36 | application_metadata | MAY carry profile-defined metadata |

The values of fields marked as application or extension data MUST NOT be interpreted as RPP mission semantics.

### 9.2 File descriptors

A file descriptor MAY use the following compact fields:

| Key | Field |
|---:|---|
| 40 | path or logical name |
| 20 | logical size |
| 41 | file hash |
| 25 | media type |
| 42 | file range |
| 43 | chunk range |

A receiver MUST treat file paths as package content, not as permission to write to a local filesystem. Local extraction policy is outside RPP.

### 9.3 Chunk descriptors

A chunk descriptor MAY use the following compact fields:

| Key | Field |
|---:|---|
| 22 | chunk identifier |
| 23 | chunk index |
| 20 | chunk size |
| 21 | chunk hash |
| 44 | offset |
| 45 | length |

Chunk indexes MUST be unambiguous within the applicable resource or package. A receiver MUST reject duplicate indexes with conflicting content.

### 9.4 Extensions

An extension MUST be identified by name or numeric identifier and MUST state whether it is critical.

A receiver that does not understand a critical extension MUST reject or quarantine the object. A receiver MAY ignore an unknown non-critical extension without changing the meaning of the core package.

## 10. Private Sharing and Discovery

### 10.1 Explicit destinations

A package offer MUST be addressed to an explicitly selected destination or to a destination authorized by an explicit grant.

A publisher MUST NOT expose package inventory, package identifiers, manifest metadata, or recipient authorization through a public broadcast inventory.

Reticulum announces MUST NOT be used for package discovery.

A normal RNS announce MAY be used for endpoint or path discovery when required by the underlying Reticulum deployment, but it MUST NOT contain or act as a public package catalog.

### 10.2 Recipient authorization

A recipient MUST be identified by its RNS destination or by a capability that is bound to the recipient destination.

A publisher MUST verify that the requested operation is authorized for the recipient and package scope.

A recipient MUST verify that an Offer, capability, manifest, or resource request is intended for it before accepting protected content.

Possession of a package identifier or manifest MUST NOT by itself grant access to a protected resource.

### 10.3 Capability tokens

A capability token MAY restrict a package or resource operation to a recipient, scope, expiry, or transfer mode.

Where a capability token is required by the package policy, the token MUST be presented and verified before the publisher serves the protected manifest or resource.

A capability MUST NOT be transferable to another destination unless the package policy explicitly permits delegation and the delegation is verifiable.

### 10.4 No global inventory requirement

RPP does not require a global package catalog. A recipient MAY learn about a package through an explicit Offer, a direct request, a local cache, a trusted application profile, or another channel that does not violate Section 10.1.

The absence of a package from a local inventory MUST NOT prove that the package does not exist.

## 11. Protocol Operations

### 11.1 Transport of control and bulk data

Small control messages MUST be carried in RNS Packet payloads or an equivalent control exchange within an RNS Link.

Manifests and bulk package resources MUST be transferable using RNS Resource operations.

RPP MUST NOT implement a second bulk-transfer protocol in place of the RNS Resource primitive.

The default transfer mode is pull: the recipient requests the manifest and resources after accepting an Offer. Push behavior MAY be added by a declared extension or package policy.

### 11.2 Transfer sequence

A conforming pull transfer follows this semantic sequence:

1. **Offer**: The publisher sends an addressed Offer identifying the package and the intended recipient scope.
2. **OfferAck**: The recipient accepts, rejects, defers, reports that it already has the package, or requests the next transfer information.
3. **ManifestRequest**: The recipient requests the manifest, with any required capability.
4. **Manifest Resource**: The publisher transfers the signed manifest using an RNS Resource.
5. **Manifest verification**: The recipient verifies CBOR, signature, package identity, expiry, authorization, and manifest consistency.
6. **MissingChunks**: The recipient identifies missing or invalid chunks after manifest verification.
7. **ResourcePlan**: The publisher proposes one or more resource or chunk bundles that fit the negotiated transfer limits.
8. **ResourceAccept**: The recipient accepts, rejects, or modifies the proposed resource transfer within its advertised limits.
9. **Chunk-bundle Resource**: The publisher transfers the accepted bundle through an RNS Resource.
10. **TransferReceipt**: The recipient reports failed, partial, complete, or complete-verified status.

Messages MAY be combined when the same semantics and authorization checks are preserved.

### 11.3 Offer

An Offer MUST identify:

- the package identifier or manifest identifier;
- the publisher destination or signing identity;
- the intended recipient or recipient scope;
- any expiry, capability, or policy needed before the next request;
- enough information for the recipient to decide whether to request the manifest.

An Offer MUST NOT be sent as an unrestricted package-discovery broadcast.

### 11.4 OfferAck

An OfferAck is a recipient response to an Offer.

It MUST identify the package and recipient destination and MUST report one of the following semantic statuses:

- rejected;
- accepted;
- already_have;
- defer;
- request_manifest;
- request_plan.

An OfferAck MAY include missing chunks, a maximum acceptable RNS Resource size, and a transfer-window limit.

The working compact object model assigns the OfferAck object type value `2` and uses fields for object type, RPP version, package identifier, manifest hash, recipient destination, timestamp, status, missing chunks, maximum resource size, and transfer window. A transport binding MUST preserve these semantics if it uses the compact object registry.

### 11.5 ManifestRequest

A ManifestRequest MUST identify the package or manifest requested and MUST include a capability token when the package policy requires one.

A publisher MUST verify destination authorization before serving the manifest.

A recipient MUST be able to request a manifest without requesting every package resource.

### 11.6 ResourcePlan

A ResourcePlan identifies a proposed transfer unit.

The working compact object model assigns the ResourcePlan object type value `4` and defines these fields:

- object type;
- RPP version;
- package identifier;
- manifest hash;
- resource identifier;
- resource kind;
- resource size;
- optional bundle identifier;
- optional bundle index;
- optional bundle count;
- optional chunk indexes;
- optional resource hash;
- optional priority;
- optional time-to-live.

A ResourcePlan MUST not exceed the negotiated resource size or transfer policy.

### 11.7 ResourceAccept

A ResourceAccept is the recipient's decision on a ResourcePlan.

It MUST identify the package, manifest, recipient, and proposed resource or bundle sufficiently to prevent acceptance of a different transfer.

It MAY accept, reject, defer, or request a smaller or different plan. A publisher MUST NOT assume acceptance merely because an RNS Link remains open.

### 11.8 MissingChunks

MissingChunks is sent after the recipient has verified the manifest and determined which chunks are absent, invalid, or unavailable locally.

The working compact object model assigns the MissingChunks object type value `7` and defines fields for object type, RPP version, package identifier, manifest hash, capability token, missing chunk indexes, maximum resource size, and transfer window.

The recipient SHOULD request missing chunks by index rather than requesting a complete package when it already holds valid chunks.

### 11.9 TransferReceipt

A TransferReceipt reports the recipient's transfer state.

The working compact object model assigns the TransferReceipt object type value `6` and defines fields for object type, RPP version, package identifier, manifest hash, recipient destination, status, received chunk count, and missing chunks.

The semantic status values are:

- failed;
- partial;
- complete;
- complete_verified;
- rejected_after_verification.

A recipient MUST use complete_verified only after all required integrity and authorization checks succeed.

## 12. Resource Transfer and Constrained Links

### 12.1 Per-resource sizing

The usable transfer unit MUST be calculated for the actual resource and link conditions.

A sender MUST account for the actual link MTU and the Reticulum and interface framing overhead, including IFAC overhead when applicable. Chunk or bundle size MUST NOT be selected solely from a compile-time constant that ignores the active link.

A receiver MAY advertise a maximum acceptable RNS Resource size. A sender MUST honor the negotiated or policy-defined maximum.

### 12.2 Adaptive transfer

A sender SHOULD adapt bundle size, resource size, and transfer window to link capacity, loss, latency, duty-cycle limits, half-duplex behavior, and available memory.

A sender MUST apply bounded serving windows and MUST NOT require a receiver to accept an unbounded number of outstanding chunks or resources.

An implementation MAY use different window algorithms, provided that it preserves bounded operation, missing-chunk recovery, and the RNS Resource semantics.

### 12.3 Resumption

A transfer MUST be resumable when the publisher still has the package and the recipient retains sufficient transfer state.

A recipient MUST be able to identify missing or invalid chunks without restarting a complete package transfer.

Active incoming parts MUST NOT be counted as timeout failures merely because the transfer is still progressing.

A sender and receiver MUST avoid repeated requests for chunks or bundle updates that are already outstanding, subject to recovery after a defined loss or expiry condition.

### 12.4 Transfer integrity

A receiver MUST verify a chunk before marking it available for completion.

A receiver MUST verify the resource and package after assembly.

A publisher MUST NOT report a transfer as complete merely because all bytes were sent; completion requires the recipient's verification result.

### 12.5 Optional compression

Compression MAY be used when declared by the manifest or transfer profile.

Compression MUST NOT change the logical package, resource, file, or chunk identity. The receiver MUST be able to distinguish compressed transfer representation from logical content and MUST verify the logical content after decompression.

## 13. Updates, Expiry, and Revocation

### 13.1 Updates

An update MUST be a new immutable package.

A manifest MAY include previous package identifiers and a sequence value. A receiver MAY use those values for update selection, but MUST NOT discard the previous package solely because a newer package exists.

Update selection is local policy unless a package profile declares a stronger requirement.

### 13.2 Expiry

A package MAY carry an expiry time.

A recipient MUST check expiry before automatic installation, automatic forwarding, or automatic use when the package policy requires expiry enforcement.

An expired package MAY remain in local storage for audit or manual inspection, but it MUST NOT be treated as current authorized content without an explicit policy decision.

### 13.3 Revocation

A package or authorization MAY carry signed revocation information.

A valid revocation MUST prevent automatic installation or automatic use of the revoked package or capability according to the applicable policy.

Revocation MUST NOT require automatic deletion of all local copies. Local deletion and retention are separate policy decisions.

RPP does not require a central revocation server. A deployment MAY distribute signed revocation data through an explicit RPP transfer or another authorized channel.

## 14. Error Handling and State

A receiver MUST reject or quarantine:

- malformed CBOR or invalid object structure;
- invalid signatures;
- digest or chunk mismatches;
- unauthorized Offers, requests, capabilities, or resources;
- expired data when expiry is required by policy;
- unknown critical extensions;
- resource plans that exceed negotiated limits;
- conflicting duplicate chunks;
- incomplete transfers presented as complete.

A temporary link failure, missing route, or unavailable publisher MUST NOT be interpreted as package deletion or package invalidity.

A transfer MAY remain partial and MAY be resumed later.

A node SHOULD expose enough transfer state to distinguish rejected, deferred, partial, failed, complete, and complete-verified outcomes.

## 15. Security Considerations

RPP security depends on explicit addressing, authenticated publisher identity, capability checks where required, deterministic signed metadata, and content verification.

A recipient MUST verify publisher signatures and content digests before accepting protected content.

A recipient MUST reject unauthorized modifications and MUST NOT treat possession of a package as proof of authority to republish, revoke, or alter it.

Offers and capabilities SHOULD include freshness, scope, recipient binding, and expiry information sufficient to limit replay. A receiver SHOULD reject replayed or expired authorization according to package policy.

RPP does not by itself define a mandatory content-encryption profile. A package MAY declare an encryption profile, but an implementation MUST reject an unknown required profile rather than treating encrypted bytes as ordinary content.

Private addressing is not the same as anonymity. Reticulum identity, routing, timing, and link metadata may reveal information depending on deployment.

## 16. Git-over-Reticulum Relationship

RPP MAY carry packages produced from Git repositories, repository snapshots, archives, bundles, or other versioned repository resources.

RPP MUST remain a generic package/resource protocol. It MUST NOT define:

- Git object formats;
- Git references;
- branch or tag negotiation;
- Git authentication semantics;
- Git merge or conflict semantics;
- repository-specific workflows.

A Git-over-Reticulum protocol MAY use RPP to transfer package or resource content. Such a protocol remains a separate protocol and MAY use RPP as its distribution layer.

The existence of Git-native support in Reticulum does not turn RPP into a Git protocol. RPP may carry a Git-related resource, but RPP's package identity, destination authorization, transfer, and integrity rules remain generic.

## 17. Extensibility

Extensions MAY add package metadata, content profiles, authorization mechanisms, resource kinds, transfer policies, or transport optimizations.

Every extension MUST be identifiable and MUST declare whether it is critical.

Unknown non-critical extensions MAY be ignored without changing the core package meaning.

Unknown critical extensions MUST cause rejection or quarantine until understood.

An extension MUST NOT use RPP core fields to introduce application-specific semantic relationships.

## 18. Versioning

Protocol versions use semantic versioning where practical:

- incompatible wire-level changes require a major version change;
- compatible protocol additions require a minor version change;
- editorial corrections may use a patch version;
- Git tags identify published specification versions;
- released tagged specifications are immutable;
- implementations SHOULD explicitly declare the RPP versions they support.

A receiver SHOULD reject a higher major protocol version that it does not support.

A receiver MAY accept a compatible lower minor version when the compatibility rules permit it.

A receiver MUST reject unknown critical extensions and MUST NOT silently reinterpret a field whose meaning changed between versions.

Package versions are content metadata and are distinct from RPP protocol versions.

## 19. Protocol Registry Considerations

RPP does not require an external IANA registry for Draft 0.1.

The specification repository MAY maintain registries for:

- RPP protocol and manifest versions;
- core CBOR object types;
- extension identifiers;
- resource kinds;
- capability profiles;
- content and compression profiles.

A registry entry MUST identify ownership, versioning, compatibility, and criticality behavior.

The compact object assignments retained from the working design include OfferAck = `2`, ResourcePlan = `4`, TransferReceipt = `6`, and MissingChunks = `7`. Any future assignment MUST avoid collision and MUST be recorded in a normative registry update.

## 20. Conformance

An implementation conforms to the RPP core when it:

1. uses RNS primitives directly for RPP control and resource transfer;
2. does not require LXMF;
3. supports deterministic CBOR for defined control and manifest structures;
4. supports SHA-256 package, manifest, resource, file, and chunk verification as applicable;
5. supports Ed25519 signature verification for signed manifests;
6. supports explicit-destination Offers;
7. does not use Reticulum announces for package discovery;
8. enforces recipient authorization and capability policy where required;
9. supports signed manifest and chunk integrity verification;
10. supports the Offer, OfferAck, ManifestRequest, resource transfer, MissingChunks, ResourcePlan, ResourceAccept, and TransferReceipt semantics;
11. supports partial and resumable transfer;
12. respects negotiated or policy-defined RNS Resource limits;
13. computes transfer units with the actual link and framing overhead;
14. distinguishes partial, failed, complete, and complete-verified states;
15. rejects malformed, unauthorized, expired, invalid, and unknown-critical data;
16. keeps application, mission, Git, RDO, and LXMF semantics outside the RPP core.

## 21. References

- RFC 2119, “Key words for use in RFCs to Indicate Requirement Levels”.
- RFC 8174, “Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words”.
- Reticulum Network Stack documentation: https://reticulum.network/
- Reticulum project repository: https://github.com/markqvist/Reticulum
- Reticulum Distributed Objects: https://github.com/FreeTAKTeam/rdo-spec
