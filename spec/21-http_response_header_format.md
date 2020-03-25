# Trace Context HTTP Response Headers Format

This section describes the binding of the distributed trace context to the `traceresponse` HTTP header.

## Traceresponse Header

The `traceresponse` HTTP response header field identifies a completed request in a tracing system. It has four fields:

* `version`
* `trace-id`
* `proposed-parent-id`
* `trace-flags`

### Header Name

Header name: `traceresponse`

In order to increase interoperability across multiple protocols and encourage successful integration, the header name SHOULD be lowercase. The header name is a single word without any delimiters, for example, a hyphen (`-`).

Vendors MUST expect the header name in any case (upper, lower, mixed), and SHOULD send the header name in lowercase.

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
version-format   = [trace-id] "-" [proposed-parent-id] "-" [trace-flags]
trace-id         = 32HEXDIGLC  ; 16 bytes array identifier. All zeroes forbidden
proposed-parent-id        = 16HEXDIGLC  ; 8 bytes array identifier. All zeroes forbidden
trace-flags      = 2HEXDIGLC   ; 8 bit flags. Currently, only one bit is used. See below for details
```

#### trace-id

This is the ID of the whole trace forest and is used to uniquely identify a <a href="#dfn-distributed-traces">distributed trace</a> through a system. It is represented as a 16-byte array, for example, `4bf92f3577b34da6a3ce929d0e0e4736`. All bytes as zero (`00000000000000000000000000000000`) is considered an invalid value.

If the `trace-id` value is invalid (for example if it contains non-allowed characters or all zeros), vendors MUST ignore the `traceresponse`.

The `trace-id` field is an optional part of the `traceresponse` response header. If the request header contains a valid `traceparent` with a `trace-id`, and the callee does not use a different `trace-id`, the callee SHOULD omit the `trace-id` field from the `traceresponse`.

See [considerations for trace-id field
generation](#considerations-for-trace-id-field-generation) for recommendations
on how to operate with `trace-id`.

#### proposed-parent-id

This is the ID of the calling request as known by the callee (in some tracing systems, this is known as the `span-id`, where a `span` is the execution of a client request). It is represented as an 8-byte array, for example, `00f067aa0ba902b7`. All bytes as zero (`0000000000000000`) is considered an invalid value.

Vendors MUST ignore the `traceresponse` when the `proposed-parent-id` is invalid (for example, if it contains non-lowercase hex characters).

The `proposed-parent-id` field is an optional part of the `traceresponse` response header. If the request header contains a valid `traceparent` with a `parent-id`, the callee SHOULD omit the `proposed-parent-id` field from the `traceresponse`.

#### trace-flags

An <a data-cite='!BIT-FIELD#firstHeading'>8-bit field</a>  that controls tracing flags such as sampling, trace level, etc. These flags are recommendations given by the callee rather than strict rules to follow for three reasons:

1. An untrusted caller may be able to abuse a tracing system by setting these flags maliciously.
2. A caller may have a bug which causes the tracing system to have a problem.
3. Different load between calling and called services might force caller to downsample.

You can find more in the section [Security considerations](#security-considerations) of this specification.

The `trace-flags` field is an optional part of the `traceresponse` response header.

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

The `tracestate` field is designed to handle the variety of techniques for making recording decisions (or other specific information) specific for a given vendor. The `sampled` flag provides better interoperability between vendors. It allows vendors to communicate recording decisions and enable a better experience for the customer.

For example, when a SaaS load balancer service participates in a <a>distributed trace</a>, this service has no knowledge of the tracing vendor used by its callee. This service may produce records of incoming requests for monitoring or troubleshooting purposes. The `sampled` flag can be used to ensure that information about requests that were marked for recording by the callee will also be recorded by the SaaS load balancer service upstream so that the callee can troubleshoot the behavior of every recorded request.

The `sampled` flag has no restrictions.

The following are a set of suggestions that vendors SHOULD use to increase vendor interoperability.

- If a component made definitive recording decision - this decision SHOULD be reflected in the `sampled` flag.
- If a component needs to make a recording decision - it SHOULD respect the `sampled` flag value.
  [Security considerations](#security-considerations) SHOULD be applied to protect from abusive or malicious use of this flag.
- If a component deferred or delayed the decision and only a subset of telemetry will be recorded, the `sampled` flag should be propagated unchanged. It should be set to `0` as the default option when the trace is initiated by this component.
- If a component receives a `0` for the `sampled` flag on an incoming request, it may still decide to record a trace. In this case it SHOULD return a `sampled` flag `1` on the response so that the caller can update its sampling decision if required.

There are two additional options that vendors MAY follow:

- A component that makes a deferred or delayed recording decision may communicate the priority of a recording by setting `sampled` flag to `1` for a subset of requests.
- A component may also fall back to probability sampling and set the `sampled` flag to `1` for the subset of requests.

##### Other Flags

The behavior of other flags, such as (`00000100`) is not defined and is reserved for future use. Vendors MUST set those to zero.


## Returning the traceresponse Field

Vendors MAY choose to include a `traceresponse` header on any response, regardless of whether or not a `traceparent` header was included on the request.

Following are suggested use cases:

### Restarted Trace

When a request crosses a trust boundary, the called service may decide to restart the trace. In this case, the called service MAY return a `traceresponse` field indicating its internal `trace-id` and sampling decision.

Example request and response:

Request
```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-d75597dee50b0cac-01
```
Response
```http
traceresponse: 00-1baad25c36c11c1e7fbd6d122bd85db6--01
```

In this example, a participant in a trace with ID `4bf92f3577b34da6a3ce929d0e0e4736` calls a third party system that collects their own internal telemetry using a new trace ID `1baad25c36c11c1e7fbd6d122bd85db6`. When the third party completes its request, it returns the new trace ID and internal sampling decision to the caller. If there is an error with the request, the caller can include the third party's internal trace ID in a support request.

**Note**: In this case, the `proposed-parent-id` was omitted from the response because, being a part of a different trace, it was not necessary for the caller.

### Load Balancer

When a request passes through a load balancer, the load balancer may wish to defer a sampling decision to its called service. In this instance, the called service MAY return a `traceresponse` field indicating its sampling decision.

Example request and response:

Request
```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-d75597dee50b0cac-00
```
Response
```http
traceresponse: 00---01
```

In this example, a caller (the load balancer) in a trace with ID `4bf92f3577b34da6a3ce929d0e0e4736` wishes to defer a sampling decision to its callee. When the callee completes the request, it returns the internal sampling decision to the caller.

**Note**: In this case, both the `proposed-parent-id` and `trace-id` were omitted from the response. Because the trace was not restarted and only a sampling decision was requested by the caller, the `proposed-parent-id` and `trace-id` were not changed.

### Web Browser
When a web browser that does not natively support trace context loads a web page, the initial page load will not contain any trace context headers. In this instance, the server MAY return a `traceresponse` field for use by a tracing tool that runs as a script in the browser.

Example response:

```http
traceresponse: 00-4bf92f3577b34da6a3ce929d0e0e4736-d75597dee50b0cac-01
```

In this example, the server is telling the browser that it should adopt trace id `4bf92f3577b34da6a3ce929d0e0e4736` and parent id `d75597dee50b0cac` for the current operation.

### Tail Sampling

When a service that made a negative sampling decision makes a call to another service, there may be some event during the processing of that request that causes the called service to decide to sample the request. In this case, it may return its updated sampling decision to the caller, the caller may also return the updated sampling decision to its caller, and so on. In this way, as much of a trace as possible may be recovered for debugging purposes even if the original sampling decision was negative.

Example request and response:

Request
```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-d75597dee50b0cac-00
```
Response
```http
traceresponse: 00---01
```
