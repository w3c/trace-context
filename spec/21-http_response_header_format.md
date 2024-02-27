# Trace Context Server Timing Metric Format

This section describes the binding of the distributed trace context to a metric in the Server Timing HTTP header.

## Trace Context Metric

The trace context metric identifies a completed request in a tracing system. It has four params:

* `tid` - required
* `cid` - required
* `v` - optional
* `flags` - optional

Example server timing header with trace context metric:

```
server-timing: trace;tid=0af7651916cd43dd8448eb211c80319c,cid=b7ad6b7169203331
```

### Metric Name

Metric name: `trace`

The metric name is [ASCII case-insensitive](https://infra.spec.whatwg.org/#ascii-case-insensitive). That is, `trace`, `Trace`, and `TRACE` are considered the same metric.

In order to increase interoperability across multiple protocols and encourage successful integration, tracing systems SHOULD encode the metric name as [ASCII lowercase](https://infra.spec.whatwg.org/#ascii-lowercase).

### Trace Context Metric Param Values

This section uses the Augmented Backus-Naur Form (ABNF) notation of [[!RFC5234]], including the DIGIT rule from that document. The `DIGIT` rule defines a single number character `0`-`9`.

```abnf
HEXDIGLC = DIGIT / "a" / "b" / "c" / "d" / "e" / "f" ; lowercase hex character
tid      = 32HEXDIGLC
cid      = 16HEXDIGLC
flags    = 2HEXDIGLC
v        = 2HEXDIGLC ; this document assumes version 00. Version ff is forbidden
```

#### Trace ID (`tid`)

The format and requirements for this are the same as those of the `trace-id` field in the `traceparent` request header. This is a required parameter.

For details, see the `trace-id` section under [traceparent Header Field Values](#traceparent-header-field-values).

#### Child ID (`cid`)

This is the span ID of the server operation. It is represented as an 8-byte array, for example, `00f067aa0ba902b7`. An all-zero child ID (`0000000000000000`) is an invalid value. Tracing systems MUST ignore the trace context metric when the child id is invalid (for example, if it contains non-lowercase hex characters).

For details, see the `span-id` section under [traceparent Header Field Values](#traceparent-header-field-values).

#### Version (`v`)

Version (`v`) is an 8-bit unsigned integer value, serialized as an ASCII string with two hexadecimal characters. Version 255 (`ff`) is invalid. This document specifies version 0 (`00`) of the trace context metric. The version field is optional; if omitted, the version is `00`.

#### Trace Flags (`flags`)

Similar to the [`trace-flags` field](#trace-flags) in the `traceparent` request header, this is a hex-encoded <a data-cite='!BIT-FIELD#firstHeading'>8-bit field</a> that provides information about how a child handled the trace. The same requirement to properly mask the bit field value when interpreting it applies here as well.

The current version of this specification (`00`) supports only two flags: `sampled` and `random-trace-id`.

These flags are recommendations given by a server, rather than strict rules for the client to follow, for three reasons:

1. An untrusted server may be able to abuse a tracing system by setting these flags maliciously.
2. A server may have a bug which causes the tracing system to have a problem.
3. Different load between services might force one or more participants to discard part or all of a trace.

You can find more in the section [Security considerations](#security-considerations) of this specification.

The trace flags param is optional. If it omitted, the value of all flags is unknown.

##### Sampled flag

When set, the least significant bit (right-most), denotes that the server may have recorded trace data. When unset, the server did not record trace data out-of-band.

The `sampled` flag provides interoperability between tracing systems. It allows tracing systems to communicate recording decisions and enable a better experience for the customer. For example, when a SaaS load balancer service participates in a <a>distributed trace</a>, this service has no knowledge of the tracing system used by the server. This service may produce records of incoming requests for monitoring or troubleshooting purposes. The `sampled` flag can be used to ensure that information about requests that were marked for recording by the server will also be recorded by the SaaS load balancer service upstream, so that the server can troubleshoot the behavior of every recorded request.

The `sampled` flag has no restrictions.

The following are a set of suggestions that tracing systems SHOULD use to increase interoperability.

- If the server made a definitive recording decision, this decision SHOULD be reflected in the `sampled` flag.
- If the server needs to make a recording decision, it SHOULD respect the `sampled` flag value.
  [Security considerations](#security-considerations) SHOULD be applied to protect from abusive or malicious use of this flag.
- If the server deferred or delayed the decision and only a subset of telemetry will be recorded, the `sampled` flag from the incoming `traceparent` header should be used if it is available. It should be set to `0` as the default option when the trace is initiated by this server.
- If the server receives a `0` for the `sampled` flag on an incoming request, it may still decide to record a trace. In this case it SHOULD return a `sampled` flag `1` on the response so that the client can update its sampling decision if required.

There are two additional options that tracing systems MAY follow:

- A server that makes a deferred or delayed recording decision may communicate the priority of a recording by setting `sampled` flag to `1` for a subset of requests.
- A server may also fall back to probability sampling and set the `sampled` flag to `1` for the subset of requests.

##### Random Trace ID Flag

The second least significant bit of the trace-flags field denotes the random-trace-id flag.

If a trace was started by a downstream participant and it responds with the trace context server timing metric, an upstream participant can use this flag to determine if the `trace-id` was generated as per
the specification for this flag.

When a participant starts or restarts a trace (that is, when the participant generates a new `trace-id`), the requirements for this flag are the same as those for the random-trace-id flag in the trace-flags field in the `traceparent` request header. For details, see the section [Random Trace ID Flag](#random-trace-id-flag).

A participant that continues a trace started upstream &mdash; that is, if the participant uses the `trace-id` value from an incoming `traceparent` header in its own trace context server timing metric &mdash; MUST set the `random-trace-id` flag in the trace context server timing metric to the same value that was found in the incoming `traceparent` header.

A participant that continues a trace started downstream &mdash; that is, if the participant uses the `trace-id` value from a trace context server timing metric it has received &mdash; MUST set the `random-trace-id` flag in its own trace context server timing metric to the same value that was found in the trace context server timing metric from which the `trace-id` was taken.

##### Other Flags

The behavior of other flags, such as (`00000100`) is not defined and is reserved for future use. Tracing systems MUST set those to zero.
