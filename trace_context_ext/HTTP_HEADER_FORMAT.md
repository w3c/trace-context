# Trace Context Extended HTTP Header Format

A correlation context header is used to pass the name-value context properties for the trace. This is a companion header for the `Trace-Context`. The values MUST be passed along to any child requests. Note that uniqueness of the key within the `Trace-Context-Ext` is not guaranteed. Context received from upstream service may be altered before passing it along.

*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*

# Format

## Header name

`Trace-Context-Ext`

Multiple correlation context headers are allowed. Values can be combined in a single header according to the [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header value

`name1[=value1[;properties1]],name2[=value2[;properties2]]`

**Limits:**
Maximum length of a combined header MUST be less than 512 bytes. 

## Name format

Url encoded string. Spaces MUST be trimmed from beginning and the end of the name. Names are case sensitive. Vendor libraries encouraged to use namespaced names of the properties to avoid conflicts.

Names `id`, `span-id`, `trace-id`, `sampled` are reserved. These properties defined in `Trace-Context` header.

## Value format

All spaces MUST be trimmed from the beginning and the end of the value. Value ends with the special character `;`, separator `,` or end of string. Value represents a url encoded string and case sensitive. 

## Properties

Since name value pairs are well-known for vendor's library - it is not recommended to use properties for `Trace-Context` key value pairs. Vendor-specific library would typically know how to parse and interpret the value for every name.

Properties are expected to be in a format of keys & key-value pairs `;` delimited list `;k1=v1;k2;k3=v3`. All unknown property names and name-value pairs MUST be preserved. 

# Examples of HTTP headers

Single header: 

```
Trace-Context-Ext: parent_application_id = 123
```

Context might be split into multiple headers:

```
Trace-Context-Ext: parent_application_id = 123
Trace-Context-Ext: trace_roads = App1%7cApp2%7cApp
```

