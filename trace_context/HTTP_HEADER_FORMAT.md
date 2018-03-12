# Trace Context HTTP Header Format

This document describes the binding of the [trace context](README.md) to `traceparent`
and `tracestate` http headers.

## Relationship between the headers

The `traceparent` header represents the incoming request in a tracing system in
a common format. The `tracestate` header includes the parent in a potentially
vendor-specific format.

For example, a client traced in the congo system adds the following headers
to an outbound http request.
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4=
```

If the receiving server is traced in the `rojo` tracing system, it carries
the over the state it received and adds a new entry with the position in
its trace.
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01,congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4=
```

You'll notice that the `rojo` system reuses the value of `traceparent` in its
entry in `tracestate`. This means it is a generic tracing system. Otherwise,
`tracestate` entries are opaque.

If the receiving server of the above is `congo` again, it continues from its
last position, overwriting its entry with one representing the new parent.

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b9c7c989f97918e1-01
tracestate: congo=Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJ5IGhpcyByZWF=,rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

Notice when `congo` wrote its `traceparent` entry, it reuses the last trace ID
which helps in consistency for those doing correlation. However, the value of
its entry `tracestate` is opaque and different. This is ok.

Finally, you'll see `tracestate` retains an entry for `rojo` exactly as it was,
except pushed to the right. The left-most position lets the next server know
which tracing system corresponds with `traceparent`. In this case, since
`congo` wrote `traceparent`, its `tracestate` entry should be left-most.

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

## Header value

`vendorName1=opaqueValue1,vendorName2=opaqueValue2`

The value a concatenation of trace graph name-state pairs. Only one entry per
name is allowed because the entry represents that last position in the trace.
Hence implementors must overwrite their entry upon reentry to their tracing
system.

For example, if tracing system name is `congo`, and a trace started in their
system, went through a system named `rojo` and later returned to `congo`, the
`tracestate` value would not be:

`congo=congosFirstPosition,rojo=rojosFirstPosition,congo=congosSecondPosition`

Rather, the entry would be rewritten to only include the most recent position:
`congo=congosSecondPosition,rojo=rojosFirstPosition`

**Limits:**
Maximum length of a combined header MUST be less than 512 bytes. 

## Name format

Name starts with the beginning of the string or separator `,` and ends with the
equal sign `=`. The contents of the name are any url encoded string that does
not contain an equal sign `=`. Names should intuitively identify a the tracing
system even if multiple systems per vendor are present.

## Value format

Value starts after equal sign and ends with a separator `,` or end of string.
In the case of a generic tracing system, it contains the same data as the most
recent `traceparent` value. Other systems may have different formatting, such
as Base64 encoded opaque values.

# Examples of HTTP headers

Single tracing system (generic format): 

```
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

Multiple tracing systems (with different formatting):

```
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01,congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4=
```

