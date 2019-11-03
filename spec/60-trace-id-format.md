## Considerations for trace-id field generation

A vendor SHOULD generate globally unique values for `trace-id`. Many unique
identification generation algorithms create IDs where one part of the value is
constant (often time- or host-based), and the other part is a randomly generated
value. Because tracing systems may make sampling decisions based on the value of
`trace-id`, for increased interoperability vendors MUST keep the random part of
`trace-id` ID on the left side.

When a system operates with a `trace-id` that is shorter than 16 bytes, it
SHOULD fill-in the extra bytes with random values rather than zeroes. Let's say
the system works with an 8-byte `trace-id` like `3ce929d0e0e4736`. Instead of
setting `trace-id` value to `0000000000000003ce929d0e0e4736` it SHOULD generate
a value like `4bf92f3577b34da6a3ce929d0e0e4736` where `4bf92f3577b34da6a` is a
random value or a function of time and host value.

**Note**: Even though a system may operate with a shorter `trace-id` for
[distributed trace](https://w3c.github.io/trace-context/#dfn-distributed-traces)
reporting, the full `trace-id` MUST be propagated to conform to the
specification.
