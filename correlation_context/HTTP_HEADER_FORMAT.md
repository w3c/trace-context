# Correlation Context HTTP Header Format

A correlation context header is used to pass the name-value context properties for the trace. This is a companion header for the `traceparent`. The values should be passed along to any child requests. Note that uniqueness of the key within the `Correlation-Context` is not guaranteed. Context received from upstream service may be altered before passing it along.

*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*

# Format

## Header name

`Correlation-Context`

Multiple correlation context headers are allowed. Values can be combined in a single header according to the [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header value

`name1=value1[;properties1],name2=value2[;properties2]`

**Limits:**
1. Maximum number of name-value pairs: `180`.
2. Maximum number of bytes per a single name-value pair: `4096`.
3. Maximum total length of all name-value pairs: `8192`.

## Name format

Url encoded string. Spaces are allows before and after the name. Header with the trimmed name and with spaces before and after name MUST be considered identical.

## Value format

Value starts after equal sign and ends with the special character `;`, separator `,` or end of string. Value represents a url encoded string and case sensitive. Spaces are allowed in the beginning and the end of the value. Value with spaces before and after MUST be considered identical to the trimmed value. 

## Properties

Properties are expected to be in a format of keys & key-value pairs `;` delimited list `;k1=v1;k2;k3=v3`. Some properties may be known to the library or platform processing the header. Such properties may effect how library or platform processes corresponding name-value pair. Properties unknown to the library or platform MUST be preserved if name and/or value wasn't modified by the library or platform.

Spaces are allowed between properties and before and after equal sign. Properties with spaces MUST be considered identical to properties with all spaces trimmed.

# Examples of HTTP headers

Single header: 

```
Correlation-Context: userId=sergey,serverNode=DF:28,isProduction=false
```

Context might be split into multiple headers:

```
Correlation-Context: userId=sergey
Correlation-Context: serverNode=DF%3D28,isProduction=false
```

Values and names might begin and end with spaces:

```
Correlation-Context: userId =   sergey
Correlation-Context: serverNode = DF%3D28, isProduction = false
```

## Example use case

For example, if all of your data needs to be sent to a single node, you could propagate a property indicating that.
```
Correlation-Context: serverNode=DF:28
```

For example, if you need to log the original user ID when making transactions arbitrarily deep into a trace.
```
Correlation-Context: userId=sergey
```

For example, if you have non-production requests that flow through the same services as production requests.
```
Correlation-Context: isProduction=false
```

