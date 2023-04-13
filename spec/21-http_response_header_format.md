# Trace Context HTTP Response Headers Format

This section describes the binding of the distributed trace context to the `traceresponse` HTTP header.

## Traceresponse Header

The `traceresponse` HTTP response header field identifies a completed request in a tracing system. It has four fields:

* `version`
* `trace-id`
* `child-id`
* `trace-flags`

### Header Name

Header name: `traceresponse`

The header name is [ASCII case-insensitive](https://infra.spec.whatwg.org/#ascii-case-insensitive). That is, `TRACERESPONSE`, `TraceResponse`, and `traceresponse` are considered the same header. The header name is a single word; it does not contain any delimiters such as a hyphen.

In order to increase interoperability across multiple protocols and encourage successful integration, tracing systems SHOULD encode the header name as [ASCII lowercase](https://infra.spec.whatwg.org/#ascii-lowercase).

### traceresponse Header Field Values

This section uses the Augmented Backus-Naur Form (ABNF) notation of [[!RFC5234]], including the DIGIT rule from that document. The `DIGIT` rule defines a single number character `0`-`9`.

``` abnf
HEXDIGLC = DIGIT / "a" / "b" / "c" / "d" / "e" / "f" ; lowercase hex character
value           = version "-" version-format
```

The dash (`-`) character is used as a delimiter between fields.

#### version

``` abnf
version         = 2HEXDIGLC   ; this document assumes version 00. Version ff is forbidden
```

Version (`version`) is an 8-bit unsigned integer value, serialized as an ASCII string with two characters. Version 255 (`"ff"`) is invalid. This document specifies version 0 (`"00"`) of the `traceresponse` header.

#### version-format

The following `version-format` definition is used for version `00`.

``` abnf
version-format   = trace-id "-" child-id "-" trace-flags
trace-id         = 32HEXDIGLC  ; 16 bytes array identifier. All zeroes forbidden
child-id         = 16HEXDIGLC  ; 8 bytes array identifier. All zeroes forbidden
trace-flags      = 2HEXDIGLC   ; 8 bit flags. See below for details
```

#### trace-id

The format and requirements for this are the same as those of the trace-id field in the `traceparent` request header.

For details, see the trace-id section under [traceparent Header Field Values](#traceparent Header Field Values).

#### child-id

This is the ID of the operation of the callee (in some tracing systems, this is known as the `span-id`, where a `span` is the execution of a client request) and is used to uniquely identify an operation within a trace. It is represented as an 8-byte array, for example, `00f067aa0ba902b7`. All bytes as zero (`0000000000000000`) is considered an invalid value.

Vendors MUST ignore the `traceresponse` when the `child-id` is invalid (for example, if it contains non-lowercase hex characters).

#### trace-flags

Similar to the `trace-flags` field in the `traceparent` request header, this field is hex-encoded.

The current version of this specification (`00`) supports only two flags: `sampled` and `random-trace-id`.

This is an <a data-cite='!BIT-FIELD#firstHeading'>8-bit field</a> that provides information about how a callee handled the trace. These flags are recommendations given by a callee rather than strict rules to follow for three reasons:

1. An untrusted callee may be able to abuse a tracing system by setting these flags maliciously.
2. A callee may have a bug which causes the tracing system to have a problem.
3. Different load between calling and called services might force one or more participants to discard part or all of a trace.

You can find more in the section [Security considerations](#security-considerations) of this specification.

##### Sampled flag

When set, the least significant bit (right-most), denotes that the callee may have recorded trace data. When unset, the callee did not record trace data out-of-band.

The `sampled` flag provides interoperability between tracing systems. It allows tracing systems to communicate recording decisions and enable a better experience for the customer. For example, when a SaaS load balancer service participates in a <a>distributed trace</a>, this service has no knowledge of the tracing system used by its callee. This service may produce records of incoming requests for monitoring or troubleshooting purposes. The `sampled` flag can be used to ensure that information about requests that were marked for recording by the callee will also be recorded by the SaaS load balancer service upstream so that the callee can troubleshoot the behavior of every recorded request.

The `sampled` flag has no restrictions.

The following are a set of suggestions that tracing systems SHOULD use to increase interoperability.

- If a component made a definitive recording decision, this decision SHOULD be reflected in the `sampled` flag.
- If a component needs to make a recording decision, it SHOULD respect the `sampled` flag value.
  [Security considerations](#security-considerations) SHOULD be applied to protect from abusive or malicious use of this flag.
- If a component deferred or delayed the decision and only a subset of telemetry will be recorded, the `sampled` flag from the incoming `traceparent` header should be used if it is available. It should be set to `0` as the default option when the trace is initiated by this component.
- If a component receives a `0` for the `sampled` flag on an incoming request, it may still decide to record a trace. In this case it SHOULD return a `sampled` flag `1` on the response so that the caller can update its sampling decision if required.

There are two additional options that tracing systems MAY follow:

- A component that makes a deferred or delayed recording decision may communicate the priority of a recording by setting `sampled` flag to `1` for a subset of requests.
- A component may also fall back to probability sampling and set the `sampled` flag to `1` for the subset of requests.

##### Random Trace ID Flag

The second least significant bit of the trace-flags field denotes the random-trace-id flag.

The format and requirements for this are the same as those of the random-trace-id flag in the trace-flags field in the `traceparent` request header.

For details, see the trace-flags section under [traceparent Header Field Values](#traceparent Header Field Values).


##### Other Flags

The behavior of other flags, such as (`00000100`) is not defined and is reserved for future use. Tracing systems MUST set those to zero.
