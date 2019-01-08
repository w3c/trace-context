# Trace context HTTP headers

This section describes the representation and propagation of the distributed
trace context through its HTTP headers `traceparent` and `tracestate`.

## Semantic

The `traceparent` header identifies an incoming request into a participating component.

The `tracestate` header contains a list of participating components as key-value
pairs, where the key identifies the component and the value contains potentially
proprietary data needed for processing by the component.
As the components append their entry to the top of the list, while shifting
other entries to the right, the left-most position implicitly tells which
tracing system corresponds with the current `traceparent`.

## Example

A software system is traced by two components called `congo` and `rojo`.

A request traced in the `congo` system adds the following headers to an outbound
HTTP request.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4
```

If the receiving server is traced in the `rojo` tracing system, it carries over
the state it received and adds a new entry to the top of `tracestate`.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
tracestate: rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01,congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4
```

If the receiving server of the above is `congo` again, it continues from its
last position, overwriting its entry with one representing the new parent.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b9c7c989f97918e1-01
tracestate: congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4,rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
```

After that, `tracestate` contains an entry for `rojo` with the same value but
pushed to the right.  According to that, since `congo` wrote `traceparent`, its
`tracestate` entry should be left-most.

## HTTP-Header field `traceparent`

The HTTP header field `traceparent` uniquely identifies a request within a
participating component.

Platforms and libraries MUST expect this header name in any casing and SHOULD
send it in lower case.

### Header value

This section uses the Augmented Backus-Naur Form (ABNF) notation of
[RFC5234](https://tools.ietf.org/html/rfc5234), including the HEXDIG rules from
that document.

``` abnf
value           = version "-" version-format
version         = 2HEXDIG   ; this document assumes version 00. Version 255 is forbidden
```

`value` is US-ASCII encoded (which is UTF-8 compliant). The `-` character (dash)
is used as  delimiter between fields.

`version` is a 8-bit unsigned integer representing 1 byte. Possible values range
from `00` to `FE`.
The current specification expects `version` to be set to `00`.

For version `00`, `version-format` is defined as follows:

``` abnf
version-format   = trace-id "-" parent-id "-" trace-flags

trace-id         = 32HEXDIG  ; 16 bytes array identifier. All zeroes forbidden
parent-id        = 16HEXDIG  ; 8 bytes array identifier. All zeroes forbidden
trace-flags      = 2HEXDIG   ; 8 bit flags. Currently only one bit is used. See
below for details
```

#### trace-id

Contains the ID of the whole trace graph as 16-byte array represented as
hexadecimal string and is used to uniquely identify a distributed trace throughout
all participating systems.

**Example:** `4bf92f3577b34da6a3ce929d0e0e4736`.

> **Note:** Many algorithms for unique ID generation are based on some constant
> part (time or host-based) and a random value. Some systems make random
> sampling decisions based on the value of `trace-id`. To increase
> interoperability, it is recommended to keep the random part on the right side
> of the `trace-id` value.

##### Rules

* A `trace-id` with all bytes set to `0` is not allowed.
* Implementations SHOULD generate globally unique values.
* Implementations HAVE TO ignore the `traceparent` if the `trace-id` does not
  comply with this specification.
* If a system operates with a shorter `trace-id` - it SHOULD fill-in the extra
  bytes with random values rather than zeros.

  **Example:**
  A system uses a 8-byte unique identifier like `3ce929d0e0e4736`. Instead of
  setting the `trace-id` value to `0000000000000003ce929d0e0e4736` it is
  recommended to generate a value like `4bf92f3577b34da6a3ce929d0e0e4736` where
  `4bf92f3577b34da6a` is a random value or a function of time & host value.
* Even though a system may internally operate with a shorter unique identifier
  for distributed trace reporting - the full `trace-id` MUST BE propagated.

#### parent-id

Contains the ID of this call as known by the caller as 8-byte array represented as
hexadecimal string.

**Example:** `00f067aa0ba902b7`.

**Note:** `parent-id` is sometimes also referred to as `span-id` as some
telemetry systems call the execution of a client call a *span*.

##### Rules

* A `parent-id` with all bytes set to `0` is not allowed.
* Implementations HAVE TO ignore the `traceparent` if the `parent-id` does not
* comply with this specification.

#### trace-flags

Contains an [8-bit field](https://en.wikipedia.org/wiki/Bit_field) that consists
of tracing flags such as sampling or trace level.

**Example:** `01`.

`trace-flags` is hex-encoded. For example, all `8` flags set would be `ff` and
no flags set would be `00`.

**Note:** Bit fields can not be interpreted by decoding the absolute hex value.
Instead, the flags need to be evaluated using bitwise operators.

**Example for evaluating `trace-flags`:**

```java
static final byte FLAG_RECORDED = 1; // 00000001
// [...]
boolean recorded = (traceFlags & FLAG_RECORDED) == FLAG_RECORDED
```

**Note:** The encoded flags are recommendations given by the caller rather than
strict rules to follow for three reasons:

1. Trust and abuse
2. Bug in caller
3. Different load between caller service and callee service might force the
   callee to downsample.

More information can be found in the security section of this specification.

The current version of the specification only supports a single flag called
`recorded`.

#### Recorded Flag (00000001)

> **NEEDS EDITING - this whole section should be reviewed for grammar and clarity.**

When set, the least significant bit documents that the caller may have recorded
trace data. A caller that does not record trace data out-of-band leaves this
flag unset.

Many distributed tracing scenarios may break when only a subset of calls within
a distributed trace were recorded. As specific load recording information about
every incoming and outgoing request becomes prohibitively expensive. Making a
random or component-specific decision for data collection leads to fragmented
data in every distributed trace. Thus, it is typical for tracing vendors and
platforms to pass the recording decision for a given distributed trace or
information needed to make this decision.

There is no consensus on what is the best algorithm to make a recording decision.
Various techniques include probability sampling (sample 1 out of 100 distributed
traced by flipping a coin), delayed decision (make collection decision based on
duration or a result of a call deferred sampling (let callee decide whether
information about this request need to be collected). There are variations and
customizations of every technique which can be tracing vendor specific or
application defined.

`tracestate` is designed to handle the variety of techniques for making recording
decisions specific to a given tracing system or a platform. The `recorded` flag
is introduced for better interoperability between vendors. It allows to
communicate a recording decision and to provide a better customer experience in
participating systems.

For example, when a SaaS services participates in a distributed trace, this
service has no knowledge of the tracing system used by its caller but it may
produce records of incoming requests for monitoring or troubleshooting purposes.
The flag `recorded` can be used to ensure that information about requests that
were marked for recording by the caller will also be recorded by SaaS service
enabling the caller to troubleshoot the behavior of every recorded request.

The `recorded` flag has no restriction on its mutations except that it can only be
mutated when `parent-id` was updated. See section "Mutating the `traceparent`
field". However there are set of recommendations for better vendor
interoperability.

##### Recommendations

1. If a component made a definitive recording decision - this decision SHOULD be
2. reflected in the `recorded` flag.
3. If a component needs to make a recording decision - it SHOULD respect the
   `recorded` flag value. Security considerations should be applied to protect
   from abusive or malicious use of this flag - see security section.
4. If a component deferred or delayed the decision and only a subset of telemetry
   will be recorded - the flag `recorded` should be propagated unchanged. And set
   to `0` as a default option when a trace is initiated by this component. There
   are two additional scenarios:
    1. A component that makes a deferred or delayed recording decision MAY
       communicate the priority of recording by setting the `recorded` flag to
       `1` for a subset of requests.
    1. A component may also fall back to probability sampling to set the `recorded`
       flag to `1` for the subset of requests.

#### Other Flags

The behavior of other flags, such as (`00000100`) is not defined and is reserved
for future use. An implementation MUST set these flags to zero.

### Examples

**Request recorded by the caller:**

```text
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
base16(version) = 00
base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(parent-id) = 00f067aa0ba902b7
base16(trace-flags) = 01  // recorded
```

**Request NOT recorded by the caller:**

```text
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
base16(version) = 00
base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(parent-id) = 00f067aa0ba902b7
base16(trace-flags) = 00  // not recorded
```

### Versioning of `traceparent`

> **FIXME - what does this mean?** Implementation is opinionated about future version of the specification.

The current version of this specification assumes that future versions of the
`traceparent` header will be additive to the current one.

> **MOVE(d) TO PROCESSING MODEL?**
An implementation should follow these rules when parsing headers with an
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

## HTTP-Header field `tracestate`

The  HTTP header field `tracestate` carries information about a requests position
in multiple distributed tracing graphs. This header complements `traceparent`.

Platforms and libraries MUST expect this header name in any casing and SHOULD send
it in lower case.

### Header value

This section uses the Augmented Backus-Naur Form (ABNF) notation of
[RFC5234](https://tools.ietf.org/html/rfc5234), including the DIGIT rule in
[appendix B.1 for RFC5234](https://tools.ietf.org/html/rfc5234#appendix-B.1).
It also includes the OWS rule from [RFC7230 section 3.2.3](https://tools.ietf.org/html/rfc7230#section-3.2.3).

A `DIGIT` is a number between `0` and `9`.

The `tracestate` field value is a `list` as defined below. The `list` is a
series of `list-member` separated by commas `,`, and a `list-member` is a
key/value pair separated by an equals sign `=`. Spaces and horizontal tabs
surrounding a `list-member` are ignored. There can be a maximum of 32
`list-member` entries in a `list`.

A simple example of a `list` with two `list-member` entries might look like:
`vendorname1=opaqueValue1,vendorname2=opaqueValue2`.

``` abnf
list  = list-member 0*31( OWS "," OWS list-member )
list-member = key "=" value
list-member = OWS
```

Identifiers are short (up to 256 characters), textual identifiers.

``` abnf
key = lcalpha 0*255( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
key = lcalpha 0*240( lcalpha / DIGIT / "_" / "-"/ "*" / "/" ) "@" lcalpha 0*13
( lcalpha / DIGIT / "_" / "-"/ "*" / "/" )
lcalpha    = %x61-7A ; a-z
```

Note that identifiers MUST begin with a lowercase letter, and can only contain
lowercase letters `a`-`z`, digits `0`-`9`, underscores `_`, dashes `-`,
asterisks `*`, and forward slashes `/`.

For multi-tenant vendor scenarios the `@` sign MAY be used to augment a `key`
with a vendor specific prefix that identifies a tenant.

**Example:**
A vendor uses the key `congo` and identifies a tenant with the id `fw529a3039`.
To distinguish traces that cross different tenants, the vendor creates a key of
the form `fw529a3039@congo`.

`value` is an opaque string with up to 256 characters printable ASCII
[RFC0020](https://www.rfc-editor.org/info/rfc20) characters (i.e., the range
0x20 to 0x7E) except comma `,` and `=`. Note that this also excludes tabs,
newlines, carriage returns, etc.

``` abnf
value    = 0*255(chr) nblk-chr
nblk-chr = %x21-2B / %x2D-3C / %x3E-7E
chr      = %x20 / nblk-chr
```

#### Rules

* If `traceparent` is invalid, `tracestate` MUST NOT be accepted. On the contrary,
  an invalid `tracestate` MUST NOT affect the proper handling of a valid
  `traceparent` header.
* Multiple `tracestate` headers are allowed. Values from multiple headers in
  incoming requests SHOULD be combined in a single header according to the
  [RFC7230](https://tools.ietf.org/html/rfc7230#page-24) and sent as a single
  header in outgoing request.
* Empty and whitespace-only `list-member` entries are allowed.
* A participating system MUST propagate AT LEAST five `list-member` entries. It
  MAY drop `list-member` entries that exceed this limit. When dropping entries,
  the system SHOULD start dropping items starting at the right side (end) of the
  list. When propagating `tracestate` with the excessive length, the assumption
  SHOULD be that the receiver will trim the list to the length of five.
* Libraries and platforms MUST accept empty `tracestate` headers, but SHOULD
  avoid sending them. The reason for allowing of empty list members in `tracestate`
  is a difficulty for implementors to recognize the empty value when multiple
  `tracestate` headers are received. Whitespace characters are allowed for similar
  reasons as some frameworks will inject whitespace after the `,` separator
  automatically even when the header is empty.

#### Limits

> **PENDING - this was changed in favor of the 5 item limit** Maximum length of
> a combined header MUST be less than 512 characters.
> This length includes commas required to separate list items. But SHOULD NOT
> include optional white space (OWA) characters.

`tracestate` field contains essential information for request correlation.
Platforms and tracing systems MUST propagate this header. Compliance with the
specification will require storing of `tracestate` as part of the request payload
or associated metadata.
> **PENDING - this was changed in favor of the 5 item limit - see rules**
Allowing the long field values can make compliance to the specification
impossible. Thus, the aggressive limit of 512 characters was chosen.
> **PENDING - this was changed in favor of the 5 item limit - see rules**
If the `tracestate` value has more than 512 characters, the tracer CAN decide to
forward the `tracestate`. When propagating `tracestate` with the excessive
length - the assumption SHOULD be that the receiver will drop this header.

## Examples

**Single tracing system (generic format):**

``` http
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

**Multiple tracing systems (with different formatting):**

``` http
tracestate: rojo=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01,congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4
```

**Handling roundtrips:**

If a tracing system key is `congo`, and a trace started in their system, went
through a system with the key `rojo` and later returned to `congo`, the following
`tracestate` would be *invalid*:

```http
// INVALID!
tracestate:congo=congosFirstPosition,rojo=rojosFirstPosition,congo=congosSecondPosition
```

The value of a concatenation of trace graph key-value pairs. Only one entry per
key is allowed because the entry represents that last position in the trace.
Hence implementors must overwrite their entry upon reentry to their tracing system.

According to that, the resulting, valid `tracestate` header would be:

```http
tracestate: congo=congosSecondPosition,rojo=rojosFirstPosition // VALID
````

## Versioning of `tracestate`

The version of `tracestate` is defined by the version prefix of the `traceparent`
header. An implementation needs to attempt to parse `tracestate` if a higher
version is detected to the best of its abilities. It is the implementor's decision
whether to use partially-parsed `tracestate` key-value pairs or not.

## Mutating the `traceparent` field

### Base mutations

> **MOVE(D) to processing model?**
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
   `recorded` flag for more information on how this flag is recommended to be used.
3. **Update `recorded`**. The value of `recorded` reflects the caller's
   recording behavior: either the trace data were dropped or may have been
   recorded out-of-band. This mutation gives the downstream tracer information
   about the likelihood its parent's information was recorded.
4. **Restarting trace**. All properties - `trace-id`, `parent-id`, `trace-flags`
   are regenerated. This mutation is used in the services defined as a front
   gate into secure networks and eliminates a potential denial of service attack
   surface.

Libraries and platforms MUST NOT make any other mutations to the `traceparent` header.

## Mutating the `tracestate` field

> **MOVE(D) to processing model?**

Library or platform receiving `tracestate` request header MUST send it to
outgoing requests. It MAY mutate the value of this header before passing to
outgoing requests. The main concept of `tracestate` mutations is that the order
of unmodified key-value pairs MUST be preserved. Modified keys MUST be moved to
the beginning of the list.

Here is the list of allowed mutations:

1. **Update key value**. The value of any key can be updated. Modified keys MUST
2. be moved to the beginning of the list. This is the most common mutation resuming
   the trace.
3. **Add new key-value pair**. New key-value pair should be added into the beginning
   of the list.
4. **Delete the key-value pair**. Any key-value pair MAY be deleted. It is highly
   discouraged to delete keys that weren't generated by the same tracing system
   or platform. Deletion of unknown key-value pair will break correlation in other
   systems. This mutation enables two scenarios. The first is proxies can block
   certain `tracestate` keys for privacy and security concerns. The second scenario
   is a truncation of long `tracestate`'s.
