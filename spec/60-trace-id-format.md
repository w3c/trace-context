## Considerations for trace-id field generation

This section suggests some best practices to consider when platform or tracing
vendor implement `trace-id` generation and propagation algorithms. These
practices will ensure better interoperability of different systems.

### Uniqueness of `trace-id`

The value of `trace-id` SHOULD be globally unique. This field is typically used
for unique identification of a <a>distributed trace</a>. It is common for
<a>distributed traces</a> to span various components, including, for example,
cloud services. Cloud services tend to serve variety of clients and have a very
high throughput of requests. So global uniqueness of `trace-id` is important,
even when local uniqueness might seem like a good solution.

### Randomness of `trace-id`

Randomly generated value of `trace-id` SHOULD be preferred over other
algorithms of generating a globally unique identifiers. Randomness of `trace-id`
addresses some [security](#security-considerations) and [privacy
concerns](#privacy-considerations) of exposing unwanted information. Randomness
also allows tracing vendors to base sampling decisions on `trace-id` field value
and avoid propagating an additional sampling context.

As shown in the next section, it is important for `trace-id` to carry
"uniqueness" and "randomness" in the right part of the `trace-id`, for better
inter-operability with some existing systems.

### Handling `trace-id` for compliant platforms with shorter internal identifiers

There are tracing systems which use a `trace-id` that is shorter than 16 bytes,
which are still willing to adopt this specification.

If such a system is capable of propagating a fully compliant `trace-id`, even
while still requiring a shorter, non-compliant identifier for internal purposes,
the system is encouraged to utilize the `tracestate` header to propagate the
additional internal identifier. However, if a system would instead prefer to use
the internal identifier as the basis for a fully compliant `trace-id`, it SHOULD
be incorporated at the as rightmost part of a `trace-id`. For example, tracing
system may receive `234a5bcd543ef3fa53ce929d0e0e4736` as a `trace-id`, hovewer
internally it will use `53ce929d0e0e4736` as an identifier.

### Interoperating with existing systems which use shorter identifiers

There are tracing systems which are not capable of propagating the entire 16
bytes of a `trace-id`. For better interoperability between a fully compliant
systems with these existing systems, the following practices are recommended:

1. When a system creates an outbound message and needs to generate a fully
   compliant 16 bytes `trace-id` from a shorter identifier, it SHOULD left pad
   the original identifier with zeroes. For example, the identifier
   `53ce929d0e0e4736`, SHOULD be converted to `trace-id` value
   `000000000000000053ce929d0e0e4736`.
2. When a system receives an inbound message and needs to convert the 16 bytes
   `trace-id` to a shorter identifier, the rightmost part of `trace-id` SHOULD
   be used as this identifier. For instance, if the value of `trace-id` was
   `234a5bcd543ef3fa53ce929d0e0e4736` on an incoming request, tracing system
   SHOULD use identifier with the value of `53ce929d0e0e4736`.

Similar transformations are expected when tracing system converts other
distributed trace context propagation formats to W3C Trace Context. Shorter
identifiers SHOULD be left padded with zeros when converted to 16 bytes
`trace-id` and rightmost part of `trace-id` SHOULD be used as a shorter
identifier.

Note, many existing systems that are not capable of propagating the whole
`trace-id` will not propagate `tracestate` header either. However, such system
can still use `tracestate` header to propagate additional data that is known by
this system. For example, some systems use two flags indicating whether
distributed trace needs to be recorded or not. In this case one flag can be send
as `sampled` flag of `traceparent` header and `tracestate` can be used to send
and receive an additional flag. Compliant systems will propagate this flag along
all other key/value pairs. Existing systems which are not capable of
`tracestate` propagation will truncate all additional values from `tracestate`
and only pass along that flag.
