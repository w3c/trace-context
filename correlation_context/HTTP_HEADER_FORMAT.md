# Correlation Context HTTP Header Format

A correlation context header is used to pass the name-value context properties for the trace. This is a companion header for the `Trace-Context`. The values should be passed along to any child requests. Note that uniqueness of the key within the `Correlation-Context` is not guaranteed. Context received from upstream service may be altered before passing it along.

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

Url encoded string. Spaces should be trimmed from beginning and the end of the name. Names are case sensitive.

## Value format

All spaces should be trimmed from the beginning and the end of the value. Value ends with the special character `;`, separator `,` or end of string. Value represents a url encoded string and case sensitive. 

## Properties

Properties are expected to be in a format of keys & key-value pairs `;` delimited list `;k1=v1;k2;k3=v3`. All unknown property names and name-value pairs should be skipped.

# Examples of HTTP headers

Single header: 

```
Correlation-Context: component=Frontend,flightName=DF:28,IsAuthenticated=true
```

Context might be split into multiple headers:

```
Correlation-Context: component=Frontend
Correlation-Context: flight%3DName=DF28,ExposurePercentage=33.33
```

Values and names might begin and end with spaces:

```
Correlation-Context: component =   Frontend
Correlation-Context: flight%3DName = DF28, ExposurePercentage = 33.33
```
