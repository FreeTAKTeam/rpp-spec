# Reticulum Package Protocol (RPP)

Protocol: Reticulum Package Protocol
Acronym: RPP
Status: Release candidate for review
Version: 0.3-rc.1
Transport: Reticulum Network Stack

## 1. Status of This Document

The **RPP 0.3 RC1** candidate combines this semantic specification with the normative [RC1 wire profile](profiles/0.3-rc1.md) and [conformance vectors](vectors/rc1.json). For RC1 the profile fixes the concrete field types, required subsets, limits and exchange options described more generally below. It supersedes Draft 0.2. It adopts [RPP-0001](proposals/RPP-0001-manifest-reuse.md) for complete chunk manifests, verified manifest reuse and receiver-driven recovery. A Draft 0.2 manifest that omits the chunk inventory cannot be used as a Draft 0.3 manifest.

Capitalized MUST, MUST NOT, SHOULD, SHOULD NOT and MAY follow RFC 2119 and RFC 8174. Network interoperability requires the RDO owner-binding and RNS Resource qualification gates in the RC1 profile.

## 2. Purpose and Scope

RPP defines an M2 package/file ontology using RDO M3 and a transfer profile for exchanging immutable packages, files, manifests and large resources over Reticulum.

RPP ontology instances are independent RDO Objects, Properties and Relationships, with canonical Destination-hash identities and single owners. Its typed operations perform owner-authorized publication, discovery-by-reference, offer, retrieval, integrity verification and receipt handling. Bulk bytes use the existing Reticulum Resource primitive rather than generating an RDO object for every chunk.

RPP remains application-neutral and does not define factual truth, source credibility, or domain-model evidence resolution. An RPP package may contain arbitrary opaque data. The RPP ontology depends on RDO; the RDO core does not depend on RPP.

## 3. Goals and Exclusions

### 3.1 Design goals

1. Define reusable package/file types over rdo:Object, rdo:Property and rdo:Relationship.
2. Use Reticulum Destination hashes as canonical RDO identities for package, manifest and file instances.
3. Make Property and Relationship instances first-class; do not embed them as authoritative fields of a Package or File.
4. Preserve content-derived identifiers for immutable bytes and manifests, distinct from RDO Object Destinations.
5. Transfer large byte streams through RNS Resources, preserving signed manifests, hashes and chunk verification.
6. Retain private destination-scoped authorization, explicit offers, pull-based transfers, bounded flow control, resumption, and receipts.
7. Avoid public catalogs, broad announces and dependence on LXMF.
8. Keep chunks and transient transfer control messages outside the addressable ontology unless independently modeled for an application reason.

### 3.2 Non-goals

RPP does not define a general M3 ontology, factual truth resolution, message transport, filesystem layout, source control protocol, globally shared inventory, distributed consensus or a replacement for RNS Resource fragmentation. RPP MUST NOT redefine RDO ownership or addressing rules.

## 4. Terminology

**RPP M2 ontology:** Domain-specific Classes, Properties and Relationships specialized from RDO M3 and defined in ontology/rpp.ttl.

**Package:** An immutable RDO Object representing a published group of content, with a stable RDO Destination and a separate content-derived package digest.

**File:** An RDO Object representing a logical file. Its Destination ID can remain stable when content versions change.

**Manifest:** An RDO Object representing a published manifest and its integrity declarations; the encoded signed manifest is also a transferable wire artifact.

**rpp:Contains / rpp:Supersedes:** Specialized rdo:Relationship types whose instances have their own Destinations and reference source/destination RDO Objects.

**rpp:ContentHash / rpp:MediaType / rpp:ByteLength:** Specialized rdo:Property types. Instances reference their source RDO Objects and have separate Destinations.

**RDO ID:** An RPP semantic instance's canonical Reticulum Destination hash; never its file or package digest.

**Package identifier / digest:** SHA-256 digest derived from the canonical unsigned package manifest with fields identified in Section 6.2 excluded.

**Manifest hash (`manifest_hash`):** The 32-byte SHA-256 digest of the exact signed deterministic CBOR manifest bytes, including keys 2 and 7, before any transport compression or RNS framing. The publisher computes this external reference after signing. It is the cache key used by offers, chunk requests and bundle plans.

**Chunk:** A content-addressed transport fragment, not a mandatory RDO Object.

**RPP Resource:** A package file/chunk/bundle logical transfer unit, distinct from RNS Resource.

**RNS Resource:** Reticulum's existing reliable bulk-transfer primitive.

**Recipient:** An explicitly authorized RNS Destination or authenticated holder of a recipient-bound capability.

**Offer / OfferAck / ManifestRequest / ResourcePlan / ResourceAccept / MissingChunks / TransferReceipt:** Transient control operations/messages, not mandatory independently published RDO objects.

**Capability token:** A recipient-bound authorization value scoped to an operation, resource and possibly expiry.

**Transfer session:** Ephemeral negotiation/retry state, not an RDO object by default.

## 5. RDO M3 Dependency and Reticulum Data Plane

### 5.1 Ontology layering

~~~text
M2:         RPP package/file ontology   DAF     R3AKT
                         \               |       /
M3:                           RDO core ontology
                                      |
Transport:                        Reticulum RNS
                           Links, Packets, Resources
~~~

The ontology defined in ontology/rpp.ttl specializes Object, Property and Relationship classes defined by RDO. RPP depends on RDO's canonical Destination-hash identity, per-object owner and remote-operation contract. RDO MUST remain usable without RPP.

RPP control requests (publication, offers, manifest retrieval, transfer negotiation and receipts) are RPP-defined operations targeting appropriate RDO object Destinations and executing under owner authorization. The binary data plane sends signed manifests and bytes over RNS Resources and MAY use RNS Link/Packet control exchanges as a binding of those RDO operations.

### 5.2 No per-chunk distributed objects

Chunks, bundle windows, retry state, transfer receipts and ephemeral control envelopes MUST NOT require unique RDO Destinations. RPP does not turn transport fragments into M1 ontology instances. Applications MAY publish persistent transfer-related RDO objects when needed, but this is optional.

### 5.3 LXMF independence

RPP does not use LXMF message semantics and MUST NOT depend on LXMF. It MAY be implemented using a library that also implements LXMF/RNS.

## 6. Package and Resource Model

### 6.1 Ontology instances

An rpp:Package, rpp:Manifest or rpp:File instance is an independent addressable rdo:Object owned by exactly one twin. An instance of rpp:Contains or rpp:Supersedes is an independently addressable Relationship, and every rpp:ContentHash, rpp:MediaType or rpp:ByteLength instance is an independently addressable Property. Creating a relationship MUST NOT mutate its endpoints.

A Package version is immutable once published. A new published package version MUST obtain a new Package Object (and thus new RDO Destination) and a new content digest if its logical content differs. A logical File Object MAY remain stable while a new content version is referenced by a new ContentHash Property version, subject to owner policy.

### 6.2 Immutable package content identity

RPP has **two separate identity domains**:

- The RDO Destination hash identifies the addressable Package, Manifest or File Object.
- SHA-256 content/manifest hashes identify specific immutable bytes.

To avoid a circular hash, the package identifier MUST be SHA-256 of deterministic CBOR encoding of the *manifest excluding key 2 (package_id) and key 7 (signature)*. After deriving the package identifier, the publisher sets key 2 and signs the deterministic CBOR manifest with only key 7 omitted. The recipient verifies both calculations and the signature. A change in package metadata or bytes requiring a different canonical manifest MUST produce a new package identifier.

### 6.3 Resources and file descriptors

An RPP Resource is a transfer unit. A chunk identifier MUST be SHA-256 of its logical chunk bytes. Resource descriptors SHOULD include size, hash and required chunk information. A file descriptor SHOULD contain a path/logical name, logical uncompressed size, digest, media type and chunk ranges when used.

Descriptors in a signed wire manifest are a compact transport snapshot and MUST NOT replace authoritative separately owned Property/Relationship instances when the corresponding semantic records are published through RDO.

### 6.4 Content remains opaque

RPP MAY carry binaries, datasets, source archives, snapshots or serialized RDO graphs. Transfer logic MUST NOT infer domain truth from the payload. Content-specific interpretation belongs to the consuming ontology/application.

## 7. Encoding

CBOR is the compact wire serialization for RPP control data and manifests. The normative M2 vocabulary is ontology/rpp.ttl. RDF/Turtle type declarations describe semantics; exchanging an RDF serialization of a File MUST NOT replace its RDO Destination identity. RPP transport manifests MAY repeat semantic information for transfer efficiency, but are not independent sources of ownership or factual truth.


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

RPP signatures authorize publication and verify immutable content metadata. They MUST NOT confer authority over another twin's RDO Objects. RDO controls the authority to mutate Package, File, Property and Relationship instances; RPP validates package bytes, recipients and transfer integrity.


### 8.1 Required algorithms

The RPP Draft 0.3 cryptographic profile uses:

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

The wire manifest is a signed representation of one published rpp:Manifest and its package content metadata. Manifest key 2 (package_id) is the content-derived digest specified by Section 6.2; it is not the RDO ID of the corresponding rpp:Package. The manifest SHOULD also permit identifying the corresponding owner-controlled RDO Package/Manifest Destinations through a versioned application profile without requiring that every transfer fragment be an RDO Object.


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
| 24 | chunk_count | MUST give the number of entries in key 32 |
| 25 | package_content_type | MAY identify a content profile |
| 26 | compression_algorithm | MAY identify compression |
| 27 | encryption_profile | MAY identify an encryption profile |
| 28 | ledger_hash | MAY identify an external package ledger |
| 29 | revocation_hash | MAY identify revocation information |
| 31 | files | MAY describe files or logical members |
| 32 | chunks | MUST enumerate every logical chunk in package order as specified in Section 9.3 |
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

The signed manifest MUST enumerate every chunk required to reconstruct the package. Key 32 is an array in package order. Each descriptor MUST include the package-wide index, logical byte length and SHA-256 digest shown below.

| Key | Field |
|---:|---|
| 23 | Required. Unsigned zero-based index equal to the descriptor's position in the array. |
| 20 | Required. Logical uncompressed byte length as a positive unsigned integer. |
| 21 | Required. SHA-256 digest of the logical chunk bytes as a 32-byte CBOR byte string. |
| 22 | Optional chunk identifier. If present, it MUST equal key 21. |
| 44 | Optional byte offset in the logical package stream. If present, it MUST equal the sum of all preceding chunk lengths. |
| 45 | Optional logical byte length. If present, it MUST equal key 20. |

A receiver MUST verify that the array length equals `chunk_count`, that indexes are consecutive from zero, and that chunk lengths sum to `total_uncompressed_size`. A package containing zero payload bytes MUST use an empty array and count zero. Equal digests at different indexes are valid when the same bytes occur more than once. The signed chunk boundaries apply for the lifetime of the manifest.

### 9.4 Extensions

An extension MUST be identified by name or numeric identifier and MUST state whether it is critical.

A receiver that does not understand a critical extension MUST reject or quarantine the object. A receiver MAY ignore an unknown non-critical extension without changing the meaning of the core package.

## 10. Private Sharing and Discovery

### 10.1 Explicit Destinations

Publication, offers and protected-content requests MUST be bound to explicitly selected RNS recipient Destinations and to the owning RDO Package/File operation Destination. RNS path resolution is used for the RDO object; no separate HTTP/IRI directory is required.

RPP MUST NOT publish a global package inventory through RNS announces. A normal RNS announce or path response MAY resolve an RDO Destination but MUST NOT become a semantic file listing. Recipients MUST verify authorization before accepting protected content.

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

### 11.1 Control operations and binary transfer

RPP defines domain operations over RDO Package/File/Manifest Destinations. Small operation-control messages MAY use RNS packets or an RNS Link and MUST preserve the owner authorization, request identity and status semantics specified by RDO.

Signed manifest bytes and bulk package resources MUST be transferable through RNS Resources. RPP MUST NOT implement its own replacement fragmentation protocol.

Pull is the default: an authorized recipient requests package metadata, then any missing bytes. Offers MAY initiate the process. Transfer control records are transient and do not require their own RDO identities.

### 11.2 Transfer sequence

1. A publisher MAY send an addressed **Offer** naming the manifest hash. An authorized receiver that already knows the reference MAY start a pull directly.
2. On a cache miss, the receiver sends **ManifestRequest**. After authorization the publisher sends the signed manifest as an RNS Resource. The receiver MUST check the expected hash when supplied, verify the signature and package ID, validate the chunk inventory, and apply expiry and authorization policy before caching the verified manifest under its hash.
3. On a verified cache hit, including after reconnect, the receiver MUST skip manifest retrieval. It checks current policy and compares its available verified chunks with the cached inventory. If it needs data, it sends **MissingChunks** for the missing or invalid indexes. This request also acknowledges the manifest. A separate **OfferAck** is optional.
4. After authorizing the request, the publisher sends a **ResourcePlan** for requested chunks within the negotiated limits. The receiver replies with **ResourceAccept** or asks for a different plan. The publisher sends each accepted bundle as an RNS Resource. The receiver verifies the chunks and repeats the request as needed.
5. If all chunks are already available, the receiver skips bundle negotiation. Once assembly, integrity and authorization checks succeed, it sends a **TransferReceipt** with status `complete_verified`. Section 11.9 defines the other outcomes.

Messages MAY be combined when the same semantics and authorization checks are preserved.

### 11.3 Offer

An Offer MUST identify:

- the manifest hash, so the receiver can check its cache before requesting bytes;
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

An OfferAck with status `request_manifest` MAY serve as a ManifestRequest if it meets Section 11.5. An OfferAck MAY carry the MissingChunks request and its limits if it satisfies Section 11.8. A bare acceptance or `request_plan` status does not authorize sending unrequested chunks.

The working compact object model assigns the OfferAck object type value `2` and uses fields for object type, RPP version, package identifier, manifest hash, recipient destination, timestamp, status, missing chunks, maximum resource size, and transfer window. A transport binding MUST preserve these semantics if it uses the compact object registry.

### 11.5 ManifestRequest

A ManifestRequest MUST identify the package or manifest requested and MUST include a capability token when the package policy requires one.

A publisher MUST verify destination authorization before serving the manifest.

The publisher MUST send the signed manifest only in response to a receiver's manifest request, including a combined request. A receiver whose verified copy was lost, evicted or found corrupt MAY request it again. Reconnection alone MUST NOT trigger a manifest resend.

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
- ordered chunk indexes for a chunk bundle;
- optional resource hash;
- optional priority;
- optional time-to-live.

A chunk-bundle plan MUST identify the requested manifest by hash and list only requested indexes, once each, in payload order. The plan MUST respect the negotiated resource size and transfer policy. The transport binding MUST associate each incoming Resource unambiguously with its accepted plan, including when multiple bundles are outstanding.

The logical bundle payload is the concatenation of the listed chunks in plan order. The manifest hash appears once in the plan and individual chunks carry no manifest or index header. After any negotiated decompression, the receiver MUST split the payload using the signed lengths, reject a length mismatch or an unassociated bundle, and verify each chunk digest before marking that index available.

### 11.7 ResourceAccept

A ResourceAccept is the recipient's decision on a ResourcePlan.

It MUST identify the package, manifest, recipient, and proposed resource or bundle sufficiently to prevent acceptance of a different transfer.

It MAY accept, reject, defer, or request a smaller or different plan. A publisher MUST NOT assume acceptance merely because an RNS Link remains open.

### 11.8 MissingChunks

MissingChunks is sent after the recipient has verified the manifest and determined which chunks are absent, invalid, or unavailable locally.

The working compact object model assigns the MissingChunks object type value `7` and defines fields for object type, RPP version, package identifier, manifest hash, capability token, missing chunk indexes, maximum resource size, and transfer window.

The receiver MUST identify the exact signed manifest by hash and request only chunks that are absent or fail verification. It MAY request a bounded subset at a time. In the missing-index list, a CBOR unsigned integer selects one index and a two-element array of unsigned integers selects the inclusive range from first to last. Selections MUST be within the manifest inventory, sorted by starting index and free of overlaps or reversed ranges. For a nonempty package with no local chunks, the receiver can select the entire inventory with a single range.

The publisher MUST validate the selection and current recipient authorization before serving bytes. It MUST send only chunks selected by the receiver and accepted under Section 11.7. An empty selection requests no chunks.

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

A sender MUST account for the actual link MTU and the Reticulum and interface framing overhead, including IFAC overhead when applicable. The sender adapts the number of published chunks per bundle to the active link. If a single requested chunk exceeds the negotiated limit, the peers must agree on a sufficient limit or defer that chunk.

A receiver MAY advertise a maximum acceptable RNS Resource size. A sender MUST honor the negotiated or policy-defined maximum.

### 12.2 Adaptive transfer

A sender SHOULD adapt bundle size, resource size, and transfer window to link capacity, loss, latency, duty-cycle limits, half-duplex behavior, and available memory.

A sender MUST apply bounded serving windows and MUST NOT require a receiver to accept an unbounded number of outstanding chunks or resources.

An implementation MAY use different window algorithms, provided that it preserves bounded operation, missing-chunk recovery, and the RNS Resource semantics.

### 12.3 Resumption

A transfer MUST be resumable when the publisher still has the package and the recipient retains sufficient transfer state.

A recipient retaining a verified manifest MUST be able to resume directly with MissingChunks on a new authorized link. It MUST derive its request from the verified bytes it still holds. A sender serving the package MUST process a resumed request under the same authorization and transfer limits as a new request, without requiring the previous session, an OfferAck or another transfer of the manifest. If the recipient has lost its manifest it requests a fresh copy and can verify retained chunks against it.

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

RPP MAY define new M2 types as subclasses of RDO Classes, Properties and Relationships without modifying RDO M3. A versioned RPP profile MAY define additional package operations, manifest metadata, compression modes or file descriptors.

An extension MUST NOT replace Reticulum Destination hashes with content digests as canonical RDO instance IDs, silently embed authoritative Property/Relationship objects, or grant nonowners permission to mutate them. Critical extensions MUST be understood before their content is accepted.

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

## 19. Protocol and Ontology Registry

The RPP specification repository maintains normative assignments for its M2 vocabulary (ontology/rpp.ttl), wire control operation values, manifest CBOR keys, extensions and application profiles. Every registry addition SHOULD identify semantic meaning, version, compatibility and criticality.

A vocabulary IRI identifies an M2 term and does not become a second RDO network identity. RNS address construction remains defined by RDO.

## 20. Conformance

An RPP Draft 0.3 implementation MUST:

1. Use the RDO M3 contract and its one-Destination/one-owner rule for every published Package, File, Manifest, Property and Relationship instance.
2. Provide specialized M2 Package, File, Manifest, Contains, Supersedes, ContentHash, MediaType and ByteLength types.
3. Keep semantic Property/Relationship instances independent of source and endpoint Objects.
4. Preserve RDO File/Object IDs separately from SHA-256 package, file, manifest and chunk digests.
5. Validate the canonical package-identifier calculation excluding keys 2 and 7, and verify signatures over the full manifest excluding key 7.
6. Support explicit recipient authorization, private offers, manifests and integrity-checked resource transfer.
7. Use RNS Resources for large bytes. Publish and validate a complete signed chunk inventory. Support cache-miss manifest retrieval, direct resume by verified manifest hash, and bounded bundles containing only receiver-requested chunks.
8. Avoid requiring new RDO Destinations for individual chunks, receipts and transfer session state.
9. Keep application semantics, epistemic conclusions and source control logic outside the RPP transfer engine.
10. Interoperate with a conforming RDO address-binding/wire implementation before claiming end-to-end RPP interoperability.

## 21. References

- RFC 2119, “Key words for use in RFCs to Indicate Requirement Levels”.
- RFC 8174, “Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words”.
- Reticulum Network Stack documentation: https://reticulum.network/
- Reticulum project repository: https://github.com/markqvist/Reticulum
- Reticulum Distributed Objects (RDO M3): https://github.com/FreeTAKTeam/ReticulumDistributedObject
- RPP M2 vocabulary: ontology/rpp.ttl in this repository.

## Appendix A. Direct LXMF delivery and RPP (informative)

This comparison covers a standard direct LXMF message large enough to travel as an RNS Resource. Both protocols use Reticulum for packet sequencing, retransmission and reassembly on an active Link. The difference matters when that Link ends and a receiver already holds some of the content. [Reticulum Resources](https://reticulum.network/manual/understanding.html#resources) · [LXMF reference implementation](https://github.com/markqvist/LXMF/blob/7dfc8353541f46e1c5aceab4849136dc28bb7855/LXMF/LXMessage.py)

| Aspect | Direct LXMF over an RNS Resource | RPP Draft 0.3 |
|---|---|---|
| Unit of delivery | One packed LXMF message, including any attached data. | One immutable package, transferred through a signed manifest and one or more requested bundles when bytes are needed. |
| First contact | The sender offers the packed message as a Resource. | An Offer identifies the manifest by hash. The receiver requests the signed manifest on a cache miss. |
| Selection of bytes | The sender selects the message. Reticulum coordinates delivery of its parts. | The receiver compares its verified chunks with the complete inventory and requests missing indexes or ranges. |
| Bundle metadata | The Resource carries the serialized message. | One accepted plan identifies the manifest and ordered chunk indexes. The payload carries the corresponding bytes. |
| Packet loss on an active Link | RNS handles retransmission and reassembly. | RNS provides the same recovery for the manifest or bundle in transit. |
| Reconnect | After a retryable Resource failure, the reference implementation queues the message for another delivery attempt. Direct LXMF defines no request for selected attachment chunks. | The receiver retains verified chunks and requests the gaps against its cached manifest. New bundles may be smaller. |
| Completion | The sender marks a direct message delivered when its Resource completes successfully. | The receiver reports `complete_verified` after package integrity and authorization checks succeed. |
| Airtime | A one-off message avoids a separate package inventory and negotiation. | The initial transfer pays for the complete inventory. A resumed pull with a verified cached copy sends zero manifest bytes and skips previously verified chunks. |

### Example of a 100-chunk package

A publisher offers a package with manifest hash `H`. The receiver requests the manifest once, verifies it, and caches its 100 descriptors, indexed 0 through 99. At reconnect, it holds 98 verified chunks. Only indexes 17 and 63 are missing.

1. The receiver sends `MissingChunks(H, [17, 63])` on the new authorized link. This notation abbreviates the control fields. The two integers select two individual indexes.
2. The publisher authorizes the request and proposes one bundle for `H` with ordered indexes `[17, 63]`. The receiver accepts. The bundle carries the bytes of chunk 17 followed by the bytes of chunk 63.
3. The receiver uses the cached lengths to split the bundle, verifies both digests, assembles the package, and sends `TransferReceipt(H, complete_verified)` after the remaining checks succeed.

The resumed exchange transmits two chunks of payload and zero manifest bytes, plus control and RNS overhead. If chunk 17 was verified and retained before another interruption, the next request is `MissingChunks(H, [63])`.
