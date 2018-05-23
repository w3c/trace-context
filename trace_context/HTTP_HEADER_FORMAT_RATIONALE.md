#  Trace context HTTP header format rationale

This document provides rationale for the decisions made, mapping the
`traceparent` and `tracestate` fields to HTTP headers.

## Lowercase concatenated header names
While HTTP headers are conventionally delimited by hyphens, the trace context
header names are not. Rather, they are lowercase concatenated "traceparent" and
"tracestate" respectively. The departure from convention is due to practical
concerns of propagation. Trace context is unlike typical http headers, which
are point-to-point and do not propagate through other systems like messaging.
Different systems have different constraints. For example, some cannot read
case insensitively, and others forbid the hyphen character. Even if we could
suggest not using the same format for such systems, we know many systems transparently
copy http headers into fields. This class of concerns only exist when we choose
to support mixed case with hyphens. By choosing not to, we open trace context
integration beyond http at the cost of a conventional distraction.

## All parts of traceparent are required

We've been discussing to make parts of `traceparent` header optional. One proposal we declined was to allow trace-id-only `traceparent` headers. The intended use was to save size for small clients (like mobile devices) initiating the call. Rationale for declining it was to avoid abuse and confusion. Suggestion on saving size is to use binary format that we want to discuss.

Making `traceoptions` optional doesn't save a lot, but makes specification more complicated. And potentially can lead to incompatible implementations which do not expect `traceoptions`.

## `tracestate`

- The names should be human readable, but values opaque. Cryptic name can
interfere with identification of the tracing system responsible for an entry.
- Multiple entries permitted, but not across multiple headers. Order identifies which entry is associated with the `traceparent`. Arbitrary non-tracing system entries is a non use case.
- The typical name will be a single word in latin and the value will be a
copy of the `traceparent` format or an opaque string.

### Size limits

Header should be small so providers can satisfy the requirement to pass the value all the time.

512 bytes looks like a reasonable compromise.

TODO: put more thoughts into it

### Forcing lower case tracestate names

Lowercase names has a few benefits:
- consistent with structured headers specification http://httpwg.org/http-extensions/draft-ietf-httpbis-header-structure.html
- make naming consistent and avoid potential interoperability issues between systems
- encourages to minimize the name size to a single word

### String encoding of names

Url encoding is low-overhead way to encode unicode characters for non-latin characters in the 
values. Url encoding keeps a single words in latin unchanged and easy readable.
