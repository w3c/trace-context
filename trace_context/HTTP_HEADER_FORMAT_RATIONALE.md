# Trace context HTTP header format rationale

This document provides rationale for the decisions made, mapping the
`traceparent` and `tracestate` fields to HTTP headers.

## Lowercase concatenated header names

While HTTP headers are conventionally delimited by hyphens, the trace context
header names are not. Rather, they are lowercase concatenated `traceparent` and
`tracestate` respectively. The departure from convention is due to practical
concerns of propagation. Trace context is unlike typical http headers, which
are point-to-point and do not propagate through other systems like messaging.
Different systems have different constraints. For example, some cannot read
case insensitively, and others forbid the hyphen character. Even if we could
suggest not using the same format for such systems, we know many systems transparently
copy http headers into fields. This class of concerns only exist when we choose
to support mixed case with hyphens. By choosing not to, we open trace context
integration beyond http at the cost of a conventional distraction.

## All parts of `traceparent` are required

We've been discussing to make parts of `traceparent` header optional. One proposal we declined was to allow trace-id-only `traceparent` headers. The intended use was to save size for small clients (like mobile devices) initiating the call. Rationale for declining it was to avoid abuse and confusion. Suggestion on saving size is to use binary format that we want to discuss.

Making `trace-flags` optional doesn't save a lot, but makes specification more complicated. And potentially can lead to incompatible implementations which do not expect `trace-flags`.

## `tracestate`

- The names should be human readable, but values opaque. Cryptic name can
interfere with identification of the tracing system responsible for an entry.
- Multiple entries permitted, but not across multiple headers. Order identifies which entry is associated with the `traceparent`. Arbitrary non-tracing system entries is a non use case.
- The typical name will be a single word in latin and the value will be a
copy of the `traceparent` format or an opaque string.

## Mutations of `tracestate`

Two questions that comes up frequently is whether the `tracestate` header HAVE TO
be mutated on every mutation of `span-id` to identify the vendor which made this
change and whether two different vendors can modify the `tracestate` entries in
a single component.

This requirement may improve interoperability between vendors. For instance,
vendor may check the first `tracestate` key and provide some additional value
for the customer by adjusting data collection in the current component via the
knowledge of a caller behavior. For instance, apply specific sampling policies
or provide an experience for customers to get data from caller's vendor. There
are more scenarios that might be simplified by strict mutation requirements.

Even though improved interoperability will enable more scenarios specification
does not restrict number of mutations of `tracestate` and doesn't require the
mutation.

Main reason for not requiring the mutation is generic tracers. Generic tracers
are tracers which doesn't need to carry any information via `tracestate` and/or
doesn't have a single back-end this data will be stored in. The only thing
generic tracer can set in `tracestate` is either a key with some constant, an
empty value or a copy of  `traceparent`. Neither of those details particularly
interesting for the callee. But requirement puts extra burden and complexity on
implementors. Another reason for not requiring a mutation is that allowing
multiple mutations may require vendors to check for more than one key anyway.

Some back-end neutral SDKs may be implemented so that destination back-end
decided via side-car or out-of-process agent configuration. In such cases
customer may decide to enable more than one headers mutations logic in
in-process SDK. Another requirement for multiple mutations is that in similar
environment where back-end destination is decided via out-of-process
configuration - certain header mutations may still be required. Example may be
smart sampling mechanisms that rely on additional data propagation in
`tracestate`.

### Size limits

#### Total size limit

Header should be small so providers can satisfy the requirement to pass the value all the time.

512 bytes looks like a reasonable compromise.

TODO: put more thoughts into it

#### Maximum number of elements

Here are some rationals and assumptions:

- the total size can be calculated 2 * num_elements - 1 (delimiters) + sum(key.size()) + sum(value.size()).
- we assume that each key will have around 4 elements (e.g. `msft`, `goog`, etc).
- we assume that each value will have 8 or more characters (e.g. one hex int32).
- based on the previous two assumptions each key-value pair will have more than 12 characters.

Based on the assumptions and rationals a maximum number of elements of 32 looks like a reasonable compromise.

### Forcing lower case tracestate names

Lowercase names has a few benefits:
- consistent with structured headers specification http://httpwg.org/http-extensions/draft-ietf-httpbis-header-structure.html
- make naming consistent and avoid potential interoperability issues between systems
- encourages to minimize the name size to a single word

### String encoding of names

Url encoding is low-overhead way to encode unicode characters for non-latin characters in the 
values. Url encoding keeps a single words in latin unchanged and easy readable.

## Vendor name in a key

Sign `@` is allowed in a key for easy parsing of vendor name out of tracestate key. Idea is that with the registry of trace vendors one can easily understand the vendor name and how to parse it's trace state. Without `@` sign parsing will be more complicated. Also `@` sign has known semantics in
addressing for protocols like ftp and e-mails.

## Versioning

Versioning options are:

1. Pass thru unknown headers
2. Re-start trace when you see unknown header
3. Try to parse trace following some rules when you see unknown header

One variation is whether original or new header you cannot recognize is preserved in `tracestate`.

- Option 1 is least favorable as it makes one bad header break entire distributed trace.
- Option 2 is better. It's easy, doesn't restrict future version in any way and re-started trace should be understood by new systems. So only one "connection" is lost. And the lost connection issue can be solved by storing original header in `tracestate`. Drawbacks are also obvious. First, single old component always breaks traces. Second, it's harder to transition without customer dissat of broken traces. 

  Storing original value also has negative effects. Valid `traceparent` is 55 characters (out of 512 allowed for `tracestate`). And "bad" headers could be much longer pushing valuable `tracestate` pairs out. Also this requirement increases the chance of abuse. When bad actor will start sending header with the version `99` that is only understood by that actor. And the fact that every system passes thru original value allows this actor to build complete solution based on this header.
- Option 3 with the fallback to option 2 seems to allow the easiest transition between versions by forcing a lot of restrictions on the future. Initial proposal was to try to parse individual parts like `trace-id` than `span-id`. Assuming `span-id` size or format may change without changing `trace-id`. However majority sees potential for abuse here. So we suggest to force future versions be additive to the current format. And if parsing fails at any stage - simply restart the trace.

## Response headers

**TL;DR;** There are many scenarios where collaboration between distributed tracing vendors require writing and reading response headers.
We can see that this can have value, but don't think right now is the right time to standardize. We decided to rather wait for
individual vendors to start collaborate over response headers and later decide which scenarios worth standardizing. Using of `traceparent` and
`tracestate` headers is not forbidden in response headers.

### Use Cases

1. Restart a trace and return new trace identification information to caller.
2. Send Tenant ID/identity of the service so caller knows where to query telemetry from.
3. Notify upstream to sample trace sending a sampling flag (+ sampling score) for delegated sampling.
4. Report back data to the caller (like server timing, method name, application type and version). E.g. for http call - caller only knows the url when server knows route information. Route information may be helpful to caller to group outgoing requests.

### Open Issues

- If standard defines response headers - are they required or optional?
- How are they propagated to the caller of the caller? Is this done via multiple hops?
- Some IoT devices may not expect relatively large response headers.

### Potential Content of a Header

- `traceparent` can be used for use cases 1 and 3 (identity and deferred sampling).
- `tracestate`-like header can be used for all use cases.

### Problems*

- Might not work in all scenarios (e.g queues).
- Not sure what processing etc. would look like.
