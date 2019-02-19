# Privacy

Requirements to propagate headers to downstream services as well as storing values of these headers opens up potential privacy concerns. Trace vendors MUST NOT use `traceparent` and `tracestate` fields for any personally identifiable or otherwise sensitive information. The only purpose of these fields is to enable trace correlation.

Trace vendors MUST assess the risk of header abuse. This section provides some considerations and initial assessment of the risk associated with storing and propagating these headers. Tracing systems or platforms may choose to inspect and remove sensitive information from the fields before allowing the tracing system to execute code that potentially can propagate or store these fields. All mutations should, however, conform to the list of mutations defined in this specification.

## Privacy of traceparent field

The `traceparent` field has a predefined set of values. These values are randomly-generated numbers. If a random number generator has any logic of using user-identifiable information like IP address - this information may be exposed. Random number generators MUST NOT rely on any information that can potentially be user-identifiable.

Another privacy risk of the `traceparent` field is an ability to correlate calls made as part of a single transaction. A downstream service may track and correlate two or more calls made in a single transaction and make assumptions about the identity of the caller of one call base on information in another call. Service initiating calls MAY choose to restart a trace while making calls that might identify caller in the downstream service.

Note, both privacy concerns of `traceparent` field are theoretical rather than practical.

## Privacy of tracestate field

The  `tracestate` field may contain any opaque value in any of the keys. The main purpose of this header is to provide additional vendor-specific trace-identification information across different distributed tracing systems. 

Tracing systems MUST NOT include any personally identifiable information in the `tracestate` header.

Platforms and tracing systems extremely sensitive to personal information exposure MAY implement selective removal of values corresponding to the unknown keys. This mutation of the `tracestate` field is not forbidden, but highly discouraged. As it defeats the purpose of this field for allowing multiple tracing systems to collaborate.
