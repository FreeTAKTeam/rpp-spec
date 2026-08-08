# Reticulum Package Protocol (RPP)

Reticulum Package Protocol defines generic, efficient distribution of packages and external resources over Reticulum Network Stack primitives. It is intended for private, explicitly addressed sharing over constrained or intermittent links and does not define application or mission semantics.

Status: Draft, version 0.1.

Read the [normative specification](SPECIFICATION.md). This repository contains the protocol specification, not a particular implementation, crate, package, or runtime library.

Protocol versions use semantic versioning where practical. Git tags identify published specification versions; tagged specifications are immutable. Incompatible wire-level changes require a major version, compatible additions require a minor version, and editorial corrections may use a patch version. Implementations should declare the RPP versions they support.

Proposed changes are documented through the process described in [proposals/](proposals/).

RPP and [RDO](https://github.com/FreeTAKTeam/rdo-spec) are sibling protocols. RPP does not depend on RDO; RDO MAY reference RPP for large external resources.

