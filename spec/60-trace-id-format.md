## Considerations for trace-id field generation

This section suggests some best practices to consider when platform or tracing
vendor implement `trace-id` generation and propagation algorithms. These
practices will ensure better interoperability of different systems.

### Uniqueness of `trace-id`

The field `trace-id` SHOULD be globally unique. This field is typically used for
unique identification of a <a>distributed trace</a>. It is common for
<a>distributed traces</a> to span various components, including, for example,
cloud services. Cloud services tend to serve variety of clients and have a very
high throughput of requests. So global uniqueness of `trace-id` is
important, even when local uniqueness might seem like a good solution.

### Randomness of `trace-id`

Randomly generated value of `trace-id` SDHOULD be preferred over other
algorithms of generating a globally unique identifiers. Randomness of `trace-id`
addresses some [secutiry](#security-considerations) and [privacy
concerns](#privacy-considerations) of exposing unwanted information. Randomness
also allows tracing vendors to base sampling decisions on `trace-id` field value
and avoid propagating an additional sampling context.

As shown in the next section, it is important for better inter-operability with
some existing systems, for `trace-id` to carry "uniqueness" and "randomness" in
the right part of the `trace-id`.

### Length of `trace-id` for the platforms operating with shorter identifiers

There are system operates with a `trace-id` that is shorter than 16 bytes,
which still willing to adopt this specification.

If such system capable of propagating an entire `trace-id`, even while operating
internally on shorter identifier, system is encouraged to utilize the
`tracestate` header to propagate shorter identifier. However, if system wants to
use a subset of trace-id bytes as an identifier - rightmost part of a `trace-id`
SHOULD be used.

There are tracing systems that are not capable to propagate the entire 16 bytes
of a `trace-id`. For better interoperability of these systems with the fully
compliant systems, the following practices are recommended:

1. Whenever a new `trace-id` needs to be generated - it SHOULD be left padded
   with zeroes. For example, for the identifier `53ce929d0e0e4736` `trace-id`
   must be set to `000000000000000053ce929d0e0e4736`.
2. On incoming `traceparent`, the rightmost part of `trace-id` SHOULD be used as
   an identifier. This identifier needs to be used for outgoing calls,
   left padded with zeroes. For instance, when the the value of `trace-id` was
   `234a5bcd543ef3fa53ce929d0e0e4736` on incoming request, all outgoing requests
   from this tracing systems will carry `trace-id` value of:
   `000000000000000053ce929d0e0e4736`.
