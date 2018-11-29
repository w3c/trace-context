# Trace context HTTP headers format

This section describes the binding of the distributed trace context to
`traceparent` and `tracestate` http headers.

## Relationship between the headers

The `traceparent` header represents the incoming request in a tracing system in
a common format. The `tracestate` header includes the parent in a potentially
vendor-specific format.

For example, a client traced in the congo system adds the following headers to
an outbound http request.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4
```

If the receiving server is traced in the `rojo` tracing system, it carries over
the state it received and adds a new entry with the position in its trace.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
tracestate: rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01,congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4
```

You'll notice that the `rojo` system reuses the value of `traceparent` in its
entry in `tracestate`. This means it is a generic tracing system. Otherwise,
`tracestate` entries are opaque.

If the receiving server of the above is `congo` again, it continues from its
last position, overwriting its entry with one representing the new parent.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b9c7c989f97918e1-01
tracestate: congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4,rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
```

Notice when `congo` wrote its `traceparent` entry, it reuses the last trace ID
which helps in consistency for those doing correlation. However, the value of
its entry `tracestate` is opaque and different. This is ok.

Finally, you'll see `tracestate` retains an entry for `rojo` exactly as it was,
except pushed to the right. The left-most position lets the next server know
which tracing system corresponds with `traceparent`. In this case, since `congo`
wrote `traceparent`, its `tracestate` entry should be left-most.

# Traceparent field

Field `traceparent` identifies the request in a tracing system.

## Header name

In order to increase interoperability across multiple protocols and encourage
successful integration by default it is recommended to keep the header name
lower case. Header name is a single word without any delimiters like hyphen
(`-`).

Header name: `traceparent`

Platforms and libraries MUST expect header name in any casing and SHOULD send
header name in lower case.

## Field value

This section uses the Augmented Backus-Naur Form (ABNF) notation of
[RFC5234](https://tools.ietf.org/html/rfc5234), including the HEXDIG rules from
that document.

``` abnf
value           = version "-" version-format
version         = 2HEXDIG   ; this document assumes version 00. Version 255 is forbidden
```

The value is US-ASCII encoded (which is UTF-8 compliant). Character `-` is used
as a delimiter between fields.

Version (`version`) is a 1 byte representing an 8-bit unsigned integer. Version
255 is invalid. Current specification assumes the `version` is set to `00`.

The following `version-format` definition is used for version `00`.

``` abnf
version-format   = trace-id "-" parent-id "-" trace-flags

trace-id         = 32HEXDIG  ; 16 bytes array identifier. All zeroes forbidden
parent-id        = 16HEXDIG  ; 8 bytes array identifier. All zeroes forbidden
trace-flags      = 2HEXDIG   ; 8 bit flags. Currently only one bit is used. See below for details
```

### Trace-id

Is the ID of the whole trace forest. It is represented as a 16-bytes array, for
example, `4bf92f3577b34da6a3ce929d0e0e4736`. All bytes `0` are considered
invalid.

`Trace-id` is used to uniquely identify a distributed trace. So implementation
should generate globally unique values. Many algorithms of unique identification
generation are based on some constant part - time or host based and a random
values. There are systems that make random sampling decisions based on the value
of `trace-id`. So to increase interoperability it is recommended to keep the
random part on the right side of `trace-id` value.

When a system operates with a shorter `trace-id` - it is recommended to fill-in
the extra bytes with random values rather than zeroes. Let's say the system
works with a 8-byte `trace-id` like `3ce929d0e0e4736`. Instead of setting
`trace-id` value to `0000000000000003ce929d0e0e4736` it is recommended to
generate a value like `4bf92f3577b34da6a3ce929d0e0e4736` where
`4bf92f3577b34da6a` is a random value or a function of time & host value. Note,
even though a system may operate with a shorter `trace-id` for distributed trace
reporting - full `trace-id` should be propagated to conform to the
specification.

Implementation HAVE TO ignore the `traceparent` when the `trace-id` is invalid.
For instance, if it contains non-allowed characters.

### Parent-id

Is the ID of this call as known by the caller. It is also known as `span-id` as
a few telemetry systems call the execution of a client call a span. It is
represented as an 8-byte array, for example, `00f067aa0ba902b7`. All bytes `0`
is considered invalid.

Implementation HAVE TO ignore the `traceparent` when the `parent-id` is invalid.
For instance, if it contains non-allowed characters.

## Trace-flags

An [8-bit field](https://en.wikipedia.org/wiki/Bit_field) that controls tracing
flags such as sampling, trace level etc. These flags are recommendations given
by the caller rather than strict rules to follow for three reasons:

1. Trust and abuse
2. Bug in caller
3. Different load between caller service and callee service might force callee
   to down sample.

You can find more in security section of this specification.

Like other fields, `trace-flags` is hex-encoded. For example, all `8` flags set
would be `ff` and no flags set would be `00`.

As this is a bit field, you cannot interpret flags by decoding the hex value and
looking at the resulting number. For example, a flag `00000001` could be encoded
as `01` in hex, or `09` in hex if present with the flag `00001000`. A common
mistake in bit fields is forgetting to mask when interpreting flags.

Here is an example of properly handing trace flags:

```java
static final byte FLAG_RECORDED = 1; // 00000001
...
boolean recorded = (traceFlags & FLAG_RECORDED) == FLAG_RECORDED
```

Current version of specification only supports a single flag called `recorded`.

### Recorded Flag (00000001)

When set, the least significant bit documents that the caller may have recorded
trace data. A caller who does not record trace data out-of-band leaves this flag
unset.

Many distributed tracing scenarios may be broken when only a subset of calls
participated in a distributed trace were recorded. At certain load recording
information about every incoming and outgoing request become prohibitively
expensive. Making a random or component-specific decision for data collection
will lead to fragmented data in every distributed trace. Thus it is typical for
tracing vendors and platforms to pass recording decision for given distributed
trace or information needed to make this decision.

There is no consensus on what is the best algorithm to make a recording
decision. Various techniques include: probability sampling (sample 1 out of 100
distributed traced by flipping a coin), delayed decision (make collection
decision based on duration or a result of a call), deferred sampling (let callee
decide whether information about this request need to be collected). There are
variations and customizations of every technique which can be tracing vendor
specific or application defined.

Field `tracestate` is designed to handle the variety of techniques for making
recording decision specific (along any other specific information) for a given
tracing system or a platform. Flag `recorded` is introduced for better
interoperability between vendors. It allows to communicate recording decision
and enable better experience for the customer.

For example, when SaaS services participate in distributed trace - this service
has no knowledge of tracing system used by it's caller. But this service may
produce records of incoming requests for monitoring or troubleshooting purposes.
Flag `recorded` can be used to ensure that information about requests that were
marked for recording by caller will also be recorded by SaaS service. So caller
can troubleshoot the behavior of every recorded request.

Flag `recorded` has no restriction on it's mutations except that it can only be
mutated when `parent-id` was updated. See section "Mutating the traceparent
field". However there are set of suggestions that will increase vendors
interoperability.

1. If component made definitive recording decision - this decision SHOULD be
   reflected in `recorded` flag.
2. If component needs to make a recording decision - it SHOULD respect
   `recorded` flag value. Security considerations should be applied to protect
   from abusive or malicious use of this flag - see security section.
3. If component deferred or delayed decision and only a subset of telemetry will
   be recorded - flag `recorded` should be propagated unchanged. And set to `0`
   as a default option when trace is initiated by this component. There are two
   additional options:
    1. Component that makes deferred or delayed recording decision may
       communicate priority of recording by setting `recorded` flag to `1` for a
       subset of requests.
    2. Component may also fall back to probability sampling to set flag
       `recorded` to `1` for the subset of requests.

### Other Flags

The behavior of other flags, such as (`00000100`) is not defined and reserved
for future use. Implementation MUST set those to zero.

## Examples of HTTP headers

*Valid traceparent when caller recorded this request:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
base16(version) = 00
base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(parent-id) = 00f067aa0ba902b7
base16(trace-flags) = 01  // recorded
```

*Valid traceparent when caller haven't recorded this request:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
base16(version) = 00
base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(parent-id) = 00f067aa0ba902b7
base16(trace-flags) = 00  // not recorded
```

## Versioning of `traceparent`

Implementation is opinionated about future version of the specification. Current
version of this specification assumes that the future versions of `traceparent`
header will be additive to the current one.

Implementation should follow the following rules when parsing headers with an
unexpected format:

1. Pass thru services should not analyze version. Pass thru service needs to
   expect that headers may have bigger size limits in the future and only
   disallow prohibitively large headers.
2. When version prefix cannot be parsed (it's not 2 hex characters followed by
   dash (`-`)), implementation should restart the trace.
3. If higher version is detected - implementation SHOULD try to parse it.
    1. If the size of header is shorter than 55 characters -implementation
       should not parse header and should restart the trace.
    2. Try parse `trace-id`: from the first dash - next 32 characters.
       Implementation MUST check 32 characters to be hex. Make sure they are
       followed by dash.
    3. Try parse `parent-id`: from the second dash at 35th position - 16
       characters. Implementation MUST check 16 characters to be hex. Make sure
       this is followed by a dash.
    4. Try parse sampling bit of `flags`:  2 characters from third dash.
       Following with either end of string or a dash. If all three values were
       parsed successfully - implementation should use them. Implementation MUST
       NOT parse or assume anything about any fields unknown for this version.
       Implementation MUST use these fields to construct the new `traceparent`
       field according to the highest version of the specification known to the
       implementation (in this specification it is `00`).

# Tracestate field

The `tracestate` HTTP header field conveys information about request position in
multiple distributed tracing graphs. This header is a companion header for the
`traceparent`. If library or platform failed to parse `traceparent` - it MUST
NOT attempt to parse the `tracestate`. Note, that opposite it not true - failure
to parse `tracestate` MUST NOT affect the parsing of `traceparent`.

## Header name

In order to increase interoperability across multiple protocols and encourage
successful integration by default it is recommended to keep the header name
lower case. Header name is a single word without any delimiters like hyphen
(`-`).

Header name: `tracestate`

Platforms and libraries MUST expect header name in any casing and SHOULD send
header name in lower case.

## Header value

Multiple `tracestate` headers are allowed. Values from multiple headers in
incoming requests SHOULD be combined in a single header according to the
[RFC7230](https://tools.ietf.org/html/rfc7230#page-24) and send as a single
header in outgoing request.

This section uses the Augmented Backus-Naur Form (ABNF) notation of
[RFC5234](https://tools.ietf.org/html/rfc5234), including the DIGIT rule in
[appendix B.1 for RFC5234](https://tools.ietf.org/html/rfc5234#appendix-B.1). It
also includes the OWS rule from [RFC7230 section
3.2.3](https://tools.ietf.org/html/rfc7230#section-3.2.3).

`DIGIT` rule defines number `0`-`9`.

The `OWS` rule defines an optional whitespace. It is used where zero or more
whitespace characters might appear. When it is preferred to improve readability - a
sender SHOULD generate the optional whitespace as a single space; otherwise,
a sender SHOULD NOT generate optional whitespace. See details in corresponding
RFC.

The `tracestate` field value is a `list` as defined below. The `list` is a
series of `list-members` separated by commas `,`, and a `list-member` is a
key/value pair separated by an equals sign `=`. Spaces and horizontal tabs
surrounding `list-member`s are ignored. There can be a maximum of 32
`list-member`s in a `list`.

Empty and whitespace-only list members are allowed. Libraries and platforms MUST
accept empty `tracestate` headers, but SHOULD avoid sending them. The reason for
allowing of empty list members in `tracestate` is a difficulty for implementor
to recognize the empty value when multiple `tracestate` headers were sent.
Whitespace characters are allowed for a similar reason as some frameworks will
inject whitespace after `,` separator automatically even in case of an empty
header.

A simple example of a `list` with two `list-member`s might look like:
`vendorname1=opaqueValue1,vendorname2=opaqueValue2`.

``` abnf
list  = list-member 0*31( OWS "," OWS list-member )
list-member = key "=" value
list-member = OWS
```

Identifiers are short (up to 256 characters) textual identifiers.

``` abnf
key = lcalpha 0*255( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
key = lcalpha 0*240( lcalpha / DIGIT / "_" / "-"/ "*" / "/" ) "@" lcalpha 0*13( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
lcalpha    = %x61-7A ; a-z
```

Note that identifiers MUST begin with a lowercase letter, and can only contain
lowercase letters `a`-`z`, digits `0`-`9`, underscores `_`, dashes `-`,
asterisks `*`, and forward slashes `/`. For multi-tenant vendors scenarios `@`
sign can be used to prefix vendor name. Suggested use is to allow set tenant id
in the beginning of key like `fw529a3039@dt` - `fw529a3039` is a tenant id and
`@dt` is a vendor name. Searching for `@dt=` would be more robust for parsing
(searching for all vendor's keys).

Value is opaque string up to 256 characters printable ASCII
[RFC0020](https://www.rfc-editor.org/info/rfc20) characters (i.e., the range
0x20 to 0x7E) except comma `,` and `=`. Note that this also excludes tabs,
newlines, carriage returns, etc.

``` abnf
value    = 0*255(chr) nblk-chr
nblk-chr = %x21-2B / %x2D-3C / %x3E-7E
chr      = %x20 / nblk-chr
```

The length of a combined header MUST be less than or equal to 512 bytes. If the
length of a combined header is more than 512 bytes it SHOULD be ignored.

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

There might be multiple `tracestate` headers in a single request
according to [RFC7230 section
3.2.2](https://tools.ietf.org/html/rfc7230#section-3.2.2). Maximum length of a
combined header MUST be less than 512 characters. This length includes commas
required to separate list items. But SHOULD NOT include optional white space
(OWA) characters.

`tracestate` field contains essential information for request correlation.
Platforms and tracing systems MUST propagate this header. Compliance with the
specification will require storing of `tracestate` as part of the request
payload or associated metadata. Allowing the long field values can make
compliance to the specification impossible. Thus, the aggressive limit of 512
characters was chosen.

If the `tracestate` value has more than 512 characters, the tracer CAN decide to
forward the `tracestate`. When propagating `tracestate` with the excessive
length - the assumption SHOULD be that the receiver will drop this header.

## Examples of HTTP headers

Single tracing system (generic format):

``` http
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

Multiple tracing systems (with different formatting):

``` http
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01,congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4
```

## Versioning of `tracestate`

Version of `tracestate` is defined by the version prefix of `traceparent`
header. Implementation needs to attempt parsing of `tracestate` if a higher
version is detected to the best of its ability. It is the implementor's decision
whether to use partially-parsed `tracestate` key-value pairs or not.

# Mutating the traceparent field

## Base mutations

Library or platform receiving `traceparent` request header MUST send it to
outgoing requests. It MAY mutate the value of this header before passing to
outgoing requests.

If the value of the `traceparent` field wasn't changed before propagation -
`tracestate` MUST NOT be modified as well. Unmodified headers propagation is
typically implemented in pass-thru services like proxies. This behavior may also
be implemented in a service which currently does not collect distributed tracing
information.

Here is the list of allowed mutations:

1. **Update `parent-id`**. The value of property `parent-id` can be set to the
   new value representing the ID of the current operation. This is the most
   typical mutation and should be considered a default.
2. **Indicate recorded state**. The value of `recorded` flag of `trace-flags`
   may be set to `1` if it had value `0` before or vice versa. `parent-id` MUST
   be set to the new value with the `recorded` flag update. See details of
   `recorded` flag for more information on how this flag is recommended to be
   used.
3. **Update `recorded`**. The value of `recorded` reflects the caller's
   recording behavior: either the trace data were dropped or may have been
   recorded out-of-band. This mutation gives the downstream tracer information
   about the likelihood its parent's information was recorded.
4. **Restarting trace**. All properties - `trace-id`, `parent-id`, `trace-flags`
   are regenerated. This mutation is used in the services defined as a front
   gate into secure networks and eliminates a potential denial of service attack
   surface.

Libraries and platforms MUST NOT make any other mutations to the `traceparent`
header.

# Mutating the tracestate field

Library or platform receiving `tracestate` request header MUST send it to
outgoing requests. It MAY mutate the value of this header before passing to
outgoing requests. The main concept of `tracestate` mutations is that the order
of unmodified key-value pairs MUST be preserved. Modified keys MUST be moved to
the beginning of the list.

Here is the list of allowed mutations:

1. **Update key value**. The value of any key can be updated. Modified keys MUST
   be moved to the beginning of the list. This is the most common mutation
   resuming the trace.
2. **Add new key-value pair**. New key-value pair should be added into the
   beginning of the list.
3. **Delete the key-value pair**. Any key-value pair MAY be deleted. It is
   highly discouraged to delete keys that weren't generated by the same tracing
   system or platform. Deletion of unknown key-value pair will break correlation
   in other systems. This mutation enables two scenarios. The first is proxies
   can block certain `tracestate` keys for privacy and security concerns. The
   second scenario is a truncation of long `tracestate`'s.
