# Privacy

Requirements to propagate headers to downstream services as well as storing values of these headers opens up potential privacy concerns. Trace vendors MUST NOT use `traceparent` and `tracestate` fields for any personally identifiable or otherwise sensitive information. The only purpose of these fields is to enable trace correlation.

Trace vendors MUST assess the risk of header abuse. This section provides some considerations and initial assessment of the risk associated with storing and propagating these headers. Tracing systems or platforms may choose to inspect and remove sensitive information from the fields before allowing the tracing system to execute code that potentially can propagate or store these fields. All mutations should, however, conform to the list of mutations defined in this specification.

## Privacy of traceparent field

The `traceparent` field has a predefined set of values. These values are randomly-generated numbers. If a random number generator has any logic of using user-identifiable information like IP address - this information may be exposed. Random number generators MUST NOT rely on any information that can potentially be user-identifiable.

Another privacy risk of the `traceparent` field is an ability to correlate calls made as part of a single transaction. A downstream service may track and correlate two or more calls made in a single transaction and make assumptions about the identity of the caller of one call base on information in another call.

Note, both privacy concerns of `traceparent` field are theoretical rather than
practical. Some service initiating or receiving a call MAY choose to restart a
`traceparent` field to eliminate those risks completely. It is recommended to
find a way to minimize number of <a>distributed trace</a> restarts to promote
interoperability of tracing vendors. Different techniques may be used. Services
may define trust boundaries of upstream and downstream connections and level of
exposure any calls may bring. For instance, only restart `traceparent` for
authentication calls from or to external services.

Services may also define an algorithm and audit mechanism to validate randomness
of incoming or outgoing random numbers in the `traceparent` field. Note, this
algorithm will be services-specific and not a part of this specification. One
example can be a temporal algorithms where reversible hash function is applied
to the current clock time. So receiver can validate that the time is in agreed
boundaries, meaning the random number was generated with the required algorithm
and in fact doesn't contain any personal identifiable information.

## Privacy of tracestate field

The `tracestate` field may contain any opaque value in any of the keys. The main purpose of this header is to provide additional vendor-specific trace-identification information across different distributed tracing systems.

Tracing systems MUST NOT include any personally identifiable information in the `tracestate` header.

Platforms and tracing systems extremely sensitive to personal information exposure MAY implement selective removal of values corresponding to the unknown keys. This mutation of the `tracestate` field is not forbidden, but highly discouraged. As it defeats the purpose of this field for allowing multiple tracing systems to collaborate.

## Other risks

In implementations where `traceparent` and `tracestate` headers are included in
responses, these values may inadvertently be passed to cross-origin callers.
Implementations should ensure that they only include these response headers when
responding to systems that participated in the trace.
