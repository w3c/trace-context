# Trace Context HTTP Header Format

This document describes the binding of the [trace context](README.md) to `traceparent`
and `tracestate` http headers.

## Relationship between the headers

The `tracestate` header is not an extension of the data in `traceparent`,
rather it is the gold copy per vendor. For example, the below hints that there
is only one trace graph and that is from the Congo service:

```
trace-parent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
trace-state: congo=BleGNlZWRzIHRo
ZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNhcm5hbCBwbGVhc3VyZS4=
```

There is one exception to the "gold copy" rule, which is when the incoming
trace is fully described in generic (`traceparent`) format. The value of
`tracestate` can be left out in this case as an optimization.

For example, the following is an example of a generic trace:
```
trace-parent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
trace-state: yelp
```


*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*

# Trace-Parent Field

## Header name

`traceparent`

## Field value

```
base16(<version>)-<version_format>
```

The value will be US-ASCII encoded (which is UTF-8 compliant). Character `-` is
used as a delimiter between fields.

### Version

Is a 1-byte representing a 8-bit unsigned integer. Version 255 reserved.

### Version = 0

#### Format

```
base16(<trace-id>)-base16(<span-id>)[-base16(<trace-options>)]
```

`trace-id` and `span-id` are required. The `trace-options` is optional. Character `-`
 is used as a delimiter between fields.

#### Trace-id

Is the ID of the whole trace forest. It is represented as a 16-bytes array, e.g., 
`4bf92f3577b34da6a3ce929d0e0e4736`. All bytes 0 is considered invalid.

Implementation may decide to completely ignore the traceparent if the trace-id is invalid.

#### Span-id

Is the ID of the caller span (parent). It is represented as a 8-bytes array, e.g., 
`00f067aa0ba902b7`. All bytes 0 is considered invalid.

Implementation may decide to completely ignore the traceparent if the span-id is invalid.

#### Trace-options

Controls tracing options such as sampling, trace level etc. It is a 1-byte representing a 8-bit 
unsigned integer. The flags are recommendations given by the caller rather than strict rules to 
follow for 3 reasons:

1. Trust and abuse.
2. Bug in caller
3. Different load between caller service and callee service might force callee to down sample.    

##### Bits behavior definition (01234567):
* The least significant bit (the 7th bit) provides recommendation whether the request should be 
traced or not (`1` recommends the request should be traced, `0` means the caller does not
make a decision to trace and the decision might be deferred). When `trace-options` is missing
the default value for this bit is `0`
* The behavior of other bits is currently undefined.

#### Examples of HTTP headers

*Valid sampled traceparent:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
base16(<Version>) = 00
base16(<TraceId>) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(<SpanId>) = 00f067aa0ba902b7
base16(<TraceOptions>) = 01  // sampled
```

*Valid not-sampled traceparent:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
base16(<Version>) = 00
base16(<TraceId>) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(<SpanId>) = 00f067aa0ba902b7
base16(<TraceOptions>) = 00  // not-sampled
```

# Trace-State Field

## Header name

`tracestate`

As multiple trace graphs can be present, multiple trace state headers are
allowed. Values can be combined in a single header according to the [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header value

`name1[=value1[;properties1]],name2[=value2[;properties2]]`

**Limits:**
Maximum length of a combined header MUST be less than 512 bytes. 

## Name format

Url encoded string. Spaces are allows before and after the name. Header with the trimmed name and with spaces before and after name MUST be considered identical.

Names `id`, `span-id`, `trace-id`, `sampled` are reserved. These properties are defined in `traceparent` header.

## Value format

Value starts after equal sign and ends with the special character `;`, separator `,` or end of string. Value represents a url encoded string and case sensitive. Spaces are allowed in the beginning and the end of the value. Value with spaces before and after MUST be considered identical to the trimmed value. 

## Properties

Properties are expected to be in a format of keys & key-value pairs `;` delimited list `;k1=v1;k2;k3=v3`. Some properties may be known to the library or platform processing the header. Such properties may effect how library or platform processes corresponding name-value pair. Properties unknown to the library or platform MUST be preserved if name and/or value wasn't modified by the library or platform.

Spaces are allowed between properties and before and after equal sign. Properties with spaces MUST be considered identical to properties with all spaces trimmed.

# Examples of HTTP headers

Single header: 

```
tracestate: parent_application_id = 123
```

Context might be split into multiple headers:

```
tracestate: parent_application_id = 123
tracestate: trace_roads = App1%7cApp2%7cApp
```
