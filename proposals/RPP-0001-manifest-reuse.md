# RPP-0001 Verified manifest reuse and receiver-driven chunk requests

Adopted in [RPP Draft 0.3](../SPECIFICATION.md).

On an intermittent link, repeating a large signed manifest consumes airtime even when the receiver has already verified it. The receiver also knows which chunk bytes survived an interruption.

The publisher signs the complete chunk inventory once and identifies that exact artifact by SHA-256. The receiver requests the manifest on a cache miss, checks its local inventory, and requests missing indexes or ranges. An accepted plan associates each bundle with the manifest and the requested chunks in payload order.

Draft 0.2 allowed incomplete chunk inventories. Publishing a conforming 0.3 manifest for such a package requires a new signed artifact and a recalculated package ID under Section 6.2. A cache hit establishes which artifact the receiver holds. The publisher still verifies authorization on each pull, and the receiver checks applicable policy and verifies the logical bytes before reporting completion.
