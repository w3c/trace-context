#  Trace Context HTTP Header Format Rationale

This document provides rationale for the decisions made, mapping the
`Trace-Parent` and `Trace-State` fields to HTTP headers.

## Lowercase Concatenated header names
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

## `tracestate`

- Should be human readable. Cryptic header will hide the fact of potential information disclosure.
- Should be appende-able (comma-separated) https://tools.ietf.org/html/rfc7230#page-24 so nodes 
can add context properties without parsing an existing headers.
- It is expected that the typical name will be a single word in latin and the value will be a 
short string in latin or a derivative of an url.

### Field name without value
There is a special case allowed when the incoming trace state is fully
described by the `traceparent` header. In this case, the `tracestate` value
can be simplified to a single value representing the name of the trace graph.

For example, the following:
```
trace-parent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
trace-state: yelp
```

Is shorthand for 
```
trace-parent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
trace-state: yelp=00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

This can help with header compression while still allowing branding, tenant, or otherwise custom labels to be used. These labels can help differentiate different systems that use the same format

### Size limits

Header should be small so providers can satisfy the requirement to pass the value all the time.

512 bytes looks like a reasonable compromise.

TODO: put more thoughts into it

### Trimming of spaces

Header should be human readable and editable. Thus spaces are allowed before and after the comma, equal sign, and semicolon 
separators. It makes human-editing of headers less error-prone. It also allows better visual separation of fields when value modified manually.

### Case sensitivity of names

There are few considerations why the names should be case sensitive:
- some keys may be a url query string parameters which are case sensitive
- forcing lower case will decrease readability of the names written in camel case

### Strings encoding

Url encoding is low-overhead way to encode unicode characters for non-latin characters in the 
values. Url encoding keeps a single words in latin unchanged and easy readable.
