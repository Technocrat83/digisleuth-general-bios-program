# Digi Prose workbook sandbox configuration v0.1

This candidate record preserves `DP_WORKBOOK_E2E_v01`: the selected Small Business
AI Control Kit workbook, its $29 USD one-time sandbox checkout configuration,
registered refund terms, and the four proposed verification cases.

**Standing: registered sandbox configured; execution blocked. All four cases are
NOT_RUN. Live release is HOLD. Paying-reader and live-collection deltas are zero.**

The Founder authorized Git recording on October 21, 2026. The scope is a public,
sanitized configuration record and candidate test plan. No runtime implementation,
test execution receipt, admission, or commercial success is supplied by this package.

## Artifact and configuration bindings

`registration.public.json` records the workbook filename, size and SHA-256.
The private workbook bytes were recomputed locally and matched that digest and
size before this record was prepared. The workbook binary remains private.

The manifest also records the SHA-256 and byte count of the complete private
source registration. Public fields were selected explicitly from that source;
private buyer addresses, payment identifiers, internal file identifiers and URLs
are omitted. The original refund text is bound by its SHA-256, while the public
text substitutes a marker for the registered support contact.

Authenticated Stripe GET inspection confirmed one sandbox line item, quantity
one, 2900 USD minor units, a one-time price and no recurring component. The link
is active and retains the registered refund version and HOLD metadata. No webhook
endpoint was configured at inspection. The observed sandbox account reports
charges and payouts disabled with verification pending. These observations apply
to the inspected sandbox and do not establish a live merchant account's state.

Stripe objects remain mutable. A later execution must recheck the intended
configuration and bind its own observations to the run.

## Proposed verification cases

| Case | Required result | Current result |
| --- | --- | --- |
| T1 Success | Correct $29 checkout, one successful test order, receipt received and opened | NOT_RUN |
| T2 Delivery | Intended buyer authenticates, downloads and opens the exact workbook; unrelated session denied | NOT_RUN |
| T3 Failed payment | No captured payment, paid confirmation or delivery entitlement; retry available | NOT_RUN |
| T4 Cancellation | No capture, paid confirmation or delivery after the fixed observation window | NOT_RUN |

Timing and observation windows remain unbound. The plan is a candidate, not a
frozen execution protocol. No test transaction or entitlement has been created
by this Git recording.

## Outstanding execution bindings

Bind an authenticated delivery route and the payment-to-delivery handler, verify
the registered buyer mailbox and session, and fix test deadlines before running
the cases. Fulfillment must verify the event signature and expected account,
mode, order, product, price, currency and paid state. Repeated notifications must
produce one entitlement per order. A success-page redirect cannot grant access.
A bearer signed URL alone does not establish buyer-only access.

The legal seller and contact addresses are Founder declarations in the private
registration. Merchant identity and mailbox operation remain unverified. Usage
or license terms are still unbound. Receipt arrival, workbook opening and access
denial require observed evidence from the intended sessions.

## Preserved boundaries

This record does not emit a To Market event or Commercial Translation Object,
change maturity, admit a source, alter a runtime, or authorize production work.
The separate $299 service route and proposed $1,500 diagnostic retain their own
admission and execution requirements. The workbook test validates neither offer.
CPFK remains HOLD and physical dispatch remains `BLOCKED_UNCONDITIONALLY`.

The recording commit supplies source identity and parent ancestry. A verified
remote commit/branch binding must be reported separately. Future test receipts
must name that source revision, their tested configuration, timestamps, raw
evidence, outcomes and unresolved limits; they must not rewrite these NOT_RUN
results as historical passes.

## Files and verification

- `registration.public.json`: sanitized candidate record and test plan.
- `SHA256SUMS.txt`: SHA-256 digests of the manifest and this README.

From this directory, run `sha256sum -c SHA256SUMS.txt` to verify the committed
documentation bytes. This check does not execute the customer workflow.
