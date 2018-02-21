# Trace Context Extended HTTP Header Format

A correlation context header is used to pass the name-value context properties for the trace. This is a companion header for the `Trace-Parent`. The values MUST be passed along to any child requests. Note that uniqueness of the key within the `Trace-State` is not guaranteed. Context received from upstream service may be altered before passing it along.

*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*

# Format

## Header name

`Trace-State`

Multiple correlation context headers are allowed. Values can be combined in a single header according to the [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header value

`name1[=value1[;properties1]],name2[=value2[;properties2]]`

**Limits:**
Maximum length of a combined header MUST be less than 512 bytes. 

## Name format

Url encoded string. Spaces are allows before and after the name. Header with the trimmed name and with spaces before and after name MUST be considered identical.

Names `id`, `span-id`, `trace-id`, `sampled` are reserved. These properties are defined in `Trace-Parent` header.

## Value format

Value starts after equal sign and ends with the special character `;`, separator `,` or end of string. Value represents a url encoded string and case sensitive. Spaces are allowed in the beginning and the end of the value. Value with spaces before and after MUST be considered identical to the trimmed value. 

## Properties

Properties are expected to be in a format of keys & key-value pairs `;` delimited list `;k1=v1;k2;k3=v3`. Some properties may be known to the library or platform processing the header. Such properties may effect how library or platform processes corresponding name-value pair. Properties unknown to the library or platform MUST be preserved if name and/or value wasn't modified by the library or platform.

Spaces are allowed between properties and before and after equal sign. Properties with spaces MUST be considered identical to properties with all spaces trimmed.

# Examples of HTTP headers

Single header: 

```
Trace-State: parent_application_id = 123
```

Context might be split into multiple headers:

```
Trace-State: parent_application_id = 123
Trace-State: trace_roads = App1%7cApp2%7cApp
```

