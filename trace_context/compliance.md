# Privacy

Requirements to propagate headers to downstream services opens a potential privacy concerns. The only way to remove this concern is to inspect and remove values from the fields values before allowing the platform or tracing system to execute code that potentially can propagate these headers. All mutations should, however, conform to the list of mutations defined in this specification.

## Privacy of traceparent field

`traceparent` field has a predefined set of values. These values are randomly-generated numbers. If random number generator has any logic of using user-identifiable information like IP address - this information may be exposed. Random number generators MUST NOT rely on any information that can potentially be user-identifieable.

Another privacy risk of `traceparent` field is an ability to correlate calls made as part of a single transaction. Downstream service may track and correlate two or more calls made in a single transaction and make assumtions about identity of caller of one call base on infromation in another call. Service initiating calls MAY choose to restart trace while making calls that might identify caller in the downstream service.

Note, both privacy concerns of `traceparent` field are theoretical rather than practical.

## Privacy of tracestate field

The field `tracestate` may contain any opaque value in any of the keys. The main purpose of this header is to provide additional information about the position of reqauest in the multiple distributed tracing graphs.

Platforms and tracing systems MUST NOT include any personal identifieable information into `tracestate` header.

Platforms and tracing systems extremely sensible for personal information exposure MAY implement selective removal of values corresponded to the unknown keys. This mutation of `tracestate` field is not forbidden, but highly discouraged. As it defeats the purpose of this field of allowing multiple tracing systems collaboration. 