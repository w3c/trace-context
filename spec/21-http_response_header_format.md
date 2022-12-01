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

The header name is [ASCII case-insensitive](https://infra.spec.whatwg.org/#ascii-case-insensitive). That is, `TRACERESPONSE`, `TraceResponse`, and `traceresponse` are considered the same header. The header name is a single word, it does not contain any delimiters such as a hyphen.

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
version         = 2HEXDIGLC   ; this document assumes version 00. Version 255 is forbidden
```

The value is US-ASCII encoded (which is UTF-8 compliant).

Version (`version`) is 1 byte representing an 8-bit unsigned integer. Version `255` is invalid. The current specification assumes the `version` is set to `00`.

#### version-format

The following `version-format` definition is used for version `00`.

``` abnf
version-format   = trace-id "-" child-id "-" trace-flags
trace-id         = 32HEXDIGLC  ; 16 bytes array identifier. All zeroes forbidden
child-id         = 16HEXDIGLC  ; 8 bytes array identifier. All zeroes forbidden
trace-flags      = 2HEXDIGLC   ; 8 bit flags. Currently, only one bit is used. See below for details
```

#### trace-id

This is the ID of the whole trace forest and is used to uniquely identify a <a href="#dfn-distributed-traces">distributed trace</a> through a system. It is represented as a 16-byte array, for example, `4bf92f3577b34da6a3ce929d0e0e4736`. All bytes as zero (`00000000000000000000000000000000`) is considered an invalid value.

If the `trace-id` value is invalid (for example if it contains non-allowed characters or all zeros), tracing systems MUST ignore the `traceresponse`.

See [considerations for trace-id field generation](#considerations-for-trace-id-field-generation) for recommendations on how to operate with `trace-id`.

#### child-id

This is the ID of the operation of the callee (in some systems known as the span id) and is used to uniquely identify an operation within a trace. It is represented as an 8-byte array, for example, `00f067aa0ba902b7`. All bytes as zero (`0000000000000000`) is considered an invalid value.

#### trace-flags

An <a data-cite='!BIT-FIELD#firstHeading'>8-bit field</a> that provides additional information about how the callee handled the trace such as sampling, trace level, etc. These flags are recommendations given by the callee rather than strict rules to follow for three reasons:

1. An untrusted callee may be able to abuse a tracing system by setting these flags maliciously.
2. A callee may have a bug which causes the tracing system to have a problem.
3. Different load between calling and called services might force one or more participants to discard part or all of a trace.

You can find more in the section [Security considerations](#security-considerations) of this specification.

Like other fields, `trace-flags` is hex-encoded. For example, all `8` flags set would be `ff` and no flags set would be `00`.

As this is a bit field, you cannot interpret flags by decoding the hex value and looking at the resulting number. For example, a flag `00000001` could be encoded as `01` in hex, or `09` in hex if the flag `00001000` was also present (`00001001` is `09`). A common mistake in bit fields is forgetting to mask when interpreting flags.

Here is an example of properly handling trace flags:

``` java
static final byte FLAG_SAMPLED = 1; // 00000001
...
boolean sampled = (traceFlags & FLAG_SAMPLED) == FLAG_SAMPLED;
```

##### Sampled flag

The current version of this specification (`00`) only supports a single flag called `sampled`.

When set, the least significant bit (right-most), denotes that the callee may have recorded trace data. When unset, the callee did not record trace data out-of-band.

The `sampled` flag provides interoperability between tracing systems. It allows tracing systems to communicate recording decisions and enable a better experience for the customer. For example, when a SaaS load balancer service participates in a <a>distributed trace</a>, this service has no knowledge of the tracing system used by its callee. This service may produce records of incoming requests for monitoring or troubleshooting purposes. The `sampled` flag can be used to ensure that information about requests that were marked for recording by the callee will also be recorded by the SaaS load balancer service upstream so that the callee can troubleshoot the behavior of every recorded request.

The `sampled` flag has no restrictions.

The following are a set of suggestions that tracing systems SHOULD use to increase interoperability.

- If a component made definitive recording decision - this decision SHOULD be reflected in the `sampled` flag.
- If a component needs to make a recording decision - it SHOULD respect the `sampled` flag value.
  [Security considerations](#security-considerations) SHOULD be applied to protect from abusive or malicious use of this flag.
- If a component deferred or delayed the decision and only a subset of telemetry will be recorded, the `sampled` flag from the incoming `traceparent` header should be used if it is available. It should be set to `0` as the default option when the trace is initiated by this component.
- If a component receives a `0` for the `sampled` flag on an incoming request, it may still decide to record a trace. In this case it SHOULD return a `sampled` flag `1` on the response so that the caller can update its sampling decision if required.

There are two additional options that tracing systems MAY follow:

- A component that makes a deferred or delayed recording decision may communicate the priority of a recording by setting `sampled` flag to `1` for a subset of requests.
- A component may also fall back to probability sampling and set the `sampled` flag to `1` for the subset of requests.

##### Other Flags

The behavior of other flags, such as (`00000100`) is not defined and is reserved for future use. tracing systems MUST set those to zero.
