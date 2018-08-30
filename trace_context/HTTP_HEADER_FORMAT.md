# Trace context HTTP headers format

This section describes the binding of the distributed trace context to `traceparent`
and `tracestate` http headers.

## Relationship between the headers

The `traceparent` header represents the incoming request in a tracing system in
a common format. The `tracestate` header includes the parent in a potentially
vendor-specific format.

For example, a client traced in the congo system adds the following headers
to an outbound http request.

```HTTP
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4=
```

If the receiving server is traced in the `rojo` tracing system, it carries
over the state it received and adds a new entry with the position in
its trace.

```HTTP
traceparent: 00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
tracestate: rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01,congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4=
```

You'll notice that the `rojo` system reuses the value of `traceparent` in its
entry in `tracestate`. This means it is a generic tracing system. Otherwise,
`tracestate` entries are opaque.

If the receiving server of the above is `congo` again, it continues from its
last position, overwriting its entry with one representing the new parent.

```HTTP
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

# TraceParent field

## Header name

In order to increase interoperability across multiple protocols and encourage successful integration by default it is recommended to keep the header name lower case. Header name is a single word without any delimiters like hyphen (`-`).

Header name: `traceparent`

Platforms and libraries MUST expect header name in any casing and SHOULD send header name in lower case.

## Field value

This section uses the Augmented Backus-Naur Form (ABNF) notation of [RFC5234](https://tools.ietf.org/html/rfc5234), including the HEXDIG rules from that document.

```abnf
value           = version "-" version-format
version         = 2HEXDIG   ; this document assumes version 00. Version 255 is forbidden
```

The value is US-ASCII encoded (which is UTF-8 compliant). Character `-` is
used as a delimiter between fields.

Version (`version`) is a 1 byte representing an 8-bit unsigned integer. Version 255 is invalid. Current specification assumes the `version` is set to `00`.

The following `version-format` definition is used for version `00`.

```abnf
version-format   = trace-id "-" span-id "-" trace-flags

trace-id         = 32HEXDIG  ; 16 bytes array identifier. All zeroes forbidden
span-id          = 16HEXDIG  ; 8 bytes array identifier. All zeroes forbidden
trace-flags      = 2HEXDIG   ; 8 bit flags. Currently only one bit is used. See below for details
```

### Trace-id

Is the ID of the whole trace forest. It is represented as a 16-bytes array, for example,
`4bf92f3577b34da6a3ce929d0e0e4736`. All bytes `0` are considered invalid.

`Trace-id` is used to uniquely identify a distributed trace. So implementation should generate globally unique
values. Many algorithms of unique identification generation are based on some constant part - time or host
based and a random values. There are systems that make random sampling decisions based on the value of `trace-id`.
So to increase interoperability it is recommended to keep the random part on the right side of `trace-id` value.

When a system operates with a shorter `trace-id` - it is recommended to fill-in the extra bytes with random values rather
than zeroes. Let's say the system works with a 8-byte `trace-id` like `3ce929d0e0e4736`. Instead of setting `trace-id`
value to `0000000000000003ce929d0e0e4736` it is recommended to generate a value like
`4bf92f3577b34da6a3ce929d0e0e4736` where `4bf92f3577b34da6a` is a random value or a function of time & host value.
Note, even though a system may operate with a shorter `trace-id` for distributed trace reporting - full `trace-id` should
be propagated to conform to the specification.

Implementation HAVE TO ignore the `traceparent` when the `trace-id` is invalid. For instance, if it contains
non-allowed characters.

### Span-id

Is the ID of the caller span (parent). It is represented as an 8-byte array, for example, 
`00f067aa0ba902b7`. All bytes `0` is considered invalid.

Implementation HAVE TO ignore the `traceparent` when the `span-id` is invalid. For instance, if it contains
non-allowed characters.

## Trace-flags

An [8-bit field](https://en.wikipedia.org/wiki/Bit_field) that controls tracing flags such
as sampling, trace level etc. These flags are recommendations given by the caller rather than
strict rules to follow for three reasons:

1. Trust and abuse.
2. Bug in caller.
3. Different load between caller service and callee service might force callee
   to down sample.

You can find more in security section of this specification.

Like other fields, `trace-flags` is hex-encoded. For example, all 8 flags set would be `ff`
and no flags set would be `00`.

As this is a bit field, you cannot interpret flags by decoding the hex value and looking at
the resulting number. For example, a flag `00000001` could be encoded as `01` in hex, or `09`
in hex if present with the flag `00001000`. A common mistake in bit fields is forgetting to
mask when interpreting flags.

Here is an example of properly handing trace flags:

```java
static final byte FLAG_REQUESTED = 1; // 00000001
...
boolean traced = (traceFlags & FLAG_REQUESTED) == FLAG_REQUESTED
```

### Flag behavior

| flag         | recorded? | requested? | recording probability | situation                                                          |
| ------------ | --------  | ---------- | --------------------- | ------------------------------------------------------------------ |
| 00000000     | no        | false      | low                   | I definitely dropped the data and no one asked for it              |
| 00000001     | no        | true       | medium                | I definitely dropped the data but someone asked for it             |
| 00000010     | maybe     | false      | medium                | Maybe I recorded this but no one asked for it yet (maybe deferred) |
| 00000011     | maybe     | true       | high                  | Maybe I recorded this and someone asked for it                     |

#### Requested Flag (00000001)

When set, the least significant bit recommends the request should be traced.
Typical use for this flag is propagating a sampling decision from the service
originating the distributed trace. For instance, if originating service has a
logic to record information about 1 of every 100 requests - the one that was
marked for recording will have this flag set to `1`.

Many distributed tracing scenarios may be broken when only small subset of calls
participated in this distributed trace were collected. Thus it is important to
follow the header mutation rules. This flag can only be changed from `0` to `1`,
and not the other way around. So the decision of one component to record will be
respected by every component.

Abuse of this flag - always setting it to `1` will - also lead to broken
scenarios. Most platforms will respect this flag, but have a protection in place
to limit the amount of collected traces. And the logic of this limiting may
differ from component to component. Thus on high volume of traces when different
components will apply different policies - most traces will not have full information.

Caller who defers a tracing decision SHOULD leaves this flag unset. Caller may
communicate the priority of deferred decision (most likely will be collected)
using `recorded` flag.

Flag `recorded` can also be used to communicate the ask to collect information
or notify that information was collected and available for querying from the
caller service.

#### Recorded Flag (00000010)

When set, the second least significant bit documents that the caller may have
recorded trace data. A caller who does not record trace data  out-of-band leaves
this flag unset.

#### Other Flags

The behavior of other flags, such as (00000100) is not defined and reserved for future use. Implementation MUST set those to zero.

## Examples of HTTP headers

*Valid traceparent when one of the upstream services requested recording:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
base16(Version) = 00
base16(Trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(Span-id) = 00f067aa0ba902b7
base16(Trace-flags) = 01  // requested
```

*Valid traceparent when one of the upstream services requested recording:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
base16(Version) = 00
base16(Trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(Span-id) = 00f067aa0ba902b7
base16(Trace-flags) = 00  // not requested
```

## Versioning of `traceparent`

Implementation is opinionated about future version of the specification. Current version of this specification assumes that the future
versions of `traceparent` header will be additive to the current one.

Implementation should follow the following rules when parsing headers with an unexpected format:

1. Pass thru services should not analyze version. Pass thru service needs to expect that headers may have bigger size limits in the future and only disallow prohibitively large headers.
2. When version prefix cannot be parsed (it's not 2 hex characters followed by dash (`-`)), implementation should restart the trace.
3. If higher version is detected - implementation SHOULD try to parse it.
  a. If the size of header is shorter than 55 characters - implementation should not parse header and should restart the trace.
  b. Try parse `trace-id`: from the first dash - next 32 characters. Implementation MUST check 32 characters to be hex. Make sure they are followed by dash.
  c. Try parse `span-id`: from the second dash at 35th position - 16 characters. Implementation MUST check 16 characters to be hex.  Make sure this is followed by a dash.
  d. Try parse sampling bit of `flags`:  2 characters from third dash. Following with either end of string or a dash.
  If all three values were parsed successfully - implementation should use them. Implementation MUST NOT parse or assume anything about any fields unknown for this version. Implementation MUST use these fields to construct the new `traceparent` field according to the highest version of the specification known to the implementation (in this specification it is `00`).

# Tracestate field

The `tracestate` HTTP header field conveys information about request position in multiple distributed tracing graphs.

## Header name

In order to increase interoperability across multiple protocols and encourage successful integration by default it is recommended to keep the header name lower case. Header name is a single word without any delimiters like hyphen (`-`).

Header name: `tracestate`

Platforms and libraries MUST expect header name in any casing and SHOULD send header name in lower case.

## Header value

This section uses the Augmented Backus-Naur Form (ABNF) notation of [RFC5234](https://tools.ietf.org/html/rfc5234), including the DIGIT rule in [appendix B.1 for RFC5234](https://tools.ietf.org/html/rfc5234#appendix-B.1). It also includes the OWS rule from [RFC7230 section 3.2.3](https://tools.ietf.org/html/rfc7230#section-3.2.3).

`DIGIT` rule defines number `0`-`9`.

The `OWS` rule defines an optional whitespace. It is used where zero or more whitespace characters might appear. When it is preferred to improve readability - a sender SHOULD generate the optional whitespace as a single space; otherwise, a sender SHOULD NOT generate optional whitespace. See details in corresponding RFC.

The `tracestate` field value is a `list` as defined below. The `list` is a series of `list-members` separated by commas `,`, and a `list-member` is a key/value pair separated by an equals sign `=`. Spaces and horizontal tabs surrounding `list-member`s are ignored. There can be a maximum of 32 `list-member`s in a `list`.

A simple example of a `list` with two `list-member`s might look like: `vendorname1=opaqueValue1,vendorname2=opaqueValue2`.

```abnf
```
list  = list-member 0*31( OWS "," OWS list-member )
list-member = key "=" value
```

Identifiers are short (up to 256 characters) textual identifiers.

```abnf
key = lcalpha 0*255( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
key = lcalpha 0*240( lcalpha / DIGIT / "_" / "-"/ "*" / "/" ) "@" lcalpha 0*13( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
lcalpha    = %x61-7A ; a-z
```

Note that identifiers MUST begin with a lowercase letter, and can only contain lowercase letters `a`-`z`, digits `0`-`9`, underscores `_`, dashes `-`, asterisks `*`, and forward slashes `/`. For multi-tenant vendors scenarios `@` sign can be used to prefix vendor name. Suggested use is to allow set tenant id in the beginning of key like `fw529a3039@dt` - `fw529a3039` is a tenant id and `@dt` is a vendor name. Searching for `@dt=` would be more robust for parsing (searching for all vendor's keys).

Value is opaque string up to 256 characters printable ASCII [RFC0020](https://www.rfc-editor.org/info/rfc20) characters (i.e., the range 0x20 to 0x7E) except comma `,` and `=`. Note that this also excludes tabs, newlines, carriage returns, etc.

```abnf
value    = 0*255(chr) nblk-chr
nblk-chr = %x21-2B / %x2D-3C / %x3E-7E
chr      = %x20 / nblk-chr
```

The length of a combined header MUST be less than or equal to 512 bytes. If the length of a combined header is more than 512 bytes it SHOULD be ignored.

Example: `vendorname1=opaqueValue1,vendorname2=opaqueValue2`

The value of a concatenation of trace graph key-value pairs. Only one entry per
key is allowed because the entry represents that last position in the trace.
Hence implementors must overwrite their entry upon reentry to their tracing
system.

For example, if tracing system name is `congo`, and a trace started in their
system, went through a system named `rojo` and later returned to `congo`, the
`tracestate` value would not be:

`congo=congosFirstPosition,rojo=rojosFirstPosition,congo=congosSecondPosition`

Rather, the entry would be rewritten to only include the most recent position:
`congo=congosSecondPosition,rojo=rojosFirstPosition`

**Limits:**
There might be multiple `tracestate` headers in a single request according to [RFC7230 section 3.2.2](https://tools.ietf.org/html/rfc7230#section-3.2.2). Maximum length of a combined header MUST be less than 512 characters. This length includes commas required to separate list items. But SHOULD NOT include optional white space (OWA) characters.

`tracestate` field contains essential information for request correlation. Platforms and tracing systems MUST propagate this header. Compliance with the specification will require storing of `tracestate` as part of the request payload or associated metadata. Allowing the long field values can make compliance to the specification impossible. Thus, the aggressive limit of 512 characters was chosen.

If the `tracestate` value has more than 512 characters, the tracer CAN decide to forward the `tracestate`. When propagating `tracestate` with the excessive length - the assumption SHOULD be that the receiver will drop this header.

## Name format

Name starts with the beginning of the string or separator `,` and ends with the
equal sign `=`. The contents of the name are any URL encoded string that does
not contain an equal sign `=`. Names should intuitively identify the tracing
system even if multiple systems per vendor are present.

## Value format

Value starts after equal sign and ends with a separator `,` or end of string.
In the case of a generic tracing system, it contains the same data as the most
recent `traceparent` value. Other systems may have different formatting, such
as Base64 encoded opaque values.

## Examples of HTTP headers

Single tracing system (generic format):

```HTTP
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

Multiple tracing systems (with different formatting):

```HTTP
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01,congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4=
```

## Versioning of `tracestate`

Version of `tracestate` is defined by the version prefix of `traceparent` header. Implementation needs to attempt parsing of `tracestate` if a higher version is detected to the best of its ability. It is the implementor's decision whether to use partially-parsed `tracestate` key-value pairs or not.

# Mutating the traceparent field

## Base mutations

Library or platform receiving `traceparent` request header MUST send it to outgoing requests. It MAY mutate the value of this header before passing to outgoing requests.

If the value of the `traceparent` field wasn't changed before propagation - `tracestate` MUST NOT be modified as well. Unmodified headers propagation is typically implemented in pass-thru services like proxies. This behavior may also be implemented in a service which currently does not collect distributed tracing information.

Here is the list of allowed mutations:

1. **Update `span-id`**. The value of property `span-id` can be regenerated. This is the most typical mutation and should be considered a default.
2. **Request trace capture**. The value of `requested` flag of `trace-flags` may be set to `1` if it had value `0` before. `span-id` MUST be regenerated with the `requested` flag update. This mutation typically happens to mark the importance of a current distributed trace collection.
3. **Update `recorded`**. The value of `recorded` reflects the caller's recording behavior: either the trace data were dropped or may have been recorded out-of-band. This mutation gives the downstream tracer information about the likelihood its parent's information was recorded.
4. **Restarting trace**. All properties - `trace-id`, `span-id`, `trace-flags` are regenerated. This mutation is used in the services defined as a front gate into secure networks and eliminates a potential denial of service attack surface. 

Libraries and platforms MUST NOT make any other mutations to the `traceparent` header.

# Mutating the tracestate field

Library or platform receiving `tracestate` request header MUST send it to outgoing requests. It MAY mutate the value of this header before passing to outgoing requests. The main concept of `tracestate` mutations is that the order of unmodified key-value pairs MUST be preserved. Modified keys MUST be moved to the beginning of the list.

Here is the list of allowed mutations:

1. **Update key value**. The value of any key can be updated. Modified keys MUST be moved to the beginning of the list. This is the most common mutation resuming the trace.
2. **Add new key-value pair**. New key-value pair should be added into the beginning of the list.
3. **Delete the key-value pair**. Any key-value pair MAY be deleted. It is highly discouraged to delete keys that weren't generated by the same tracing system or platform. Deletion of unknown key-value pair will break correlation in other systems. This mutation enables two scenarios. The first is proxies can block certain `tracestate` keys for privacy and security concerns. The second scenario is a truncation of long `tracestate`'s.