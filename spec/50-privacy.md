# Privacy Considerations

Requirements to propagate headers to downstream services, as well as storing values of these headers, open up potential privacy concerns. Tracing vendors MUST NOT use `traceparent` and `tracestate` fields for any personally identifiable or otherwise sensitive information. The only purpose of these fields is to enable trace correlation.

Vendors MUST assess the risk of header abuse. This section provides some considerations and initial assessment of the risk associated with storing and propagating these headers. Tracing vendors may choose to inspect and remove sensitive information from the fields before allowing the tracing system to execute code that can potentially propagate or store these fields. All mutations should, however, conform to the list of mutations defined in this specification.

## Privacy of traceparent field

The `traceparent` field is comprised of randomly-generated numbers. If a random number generator leverages any user identifiable information like IP address as seed state, this information may be exposed. Random number generators MUST NOT rely on any information that can potentially be user-identifiable.

Another privacy risk of the `traceparent` field is the ability to correlate requests made as part of a single transaction. A downstream service may track and correlate two or more requests made in a single transaction and may make assumptions about the identity of the caller of a request based on information from another request.

Note that these privacy concerns of the `traceparent` field are theoretical rather than practical. Some services initiating or receiving a request MAY choose to restart a `traceparent` field to eliminate those risks completely. Vendors SHOULD find a way to minimize the number of <a>distributed trace</a> restarts to promote interoperability of tracing vendors. Instead of restarts, different techniques may be used. For example, services may define trust boundaries of upstream and downstream connections and the level of exposure that any requests may bring. For instance, a vendor might only restart `traceparent` for authentication requests from or to external services.

Services may also define an algorithm and audit mechanism to validate the randomness of incoming or outgoing random numbers in the `traceparent` field. Note that this algorithm is services-specific and not a part of this specification. One example might be a temporal algorithm where a reversible hash function is applied to the current clock time. The receiver can validate that the time is within agreed upon boundaries, meaning the random number was generated with the required algorithm and in fact doesn't contain any personally identifiable information.

## Privacy of tracestate field

The `tracestate` field may contain any opaque value in any of the keys. The main purpose of this header is to provide additional vendor-specific trace-identification information across different distributed tracing systems.

Vendors MUST NOT include any personally identifiable information in the `tracestate` header.

Vendors extremely sensitive to personal information exposure MAY implement selective removal of values corresponding to the unknown keys. Vendors SHOULD NOT mutate the `tracestate` field, as it defeats the purpose of allowing multiple tracing systems to collaborate.

## Other risks

When vendors include `traceparent` and `tracestate` headers in responses, these values may inadvertently be passed to cross-origin callers. Vendors should ensure that they include only these response headers when responding to systems that participated in the trace.
