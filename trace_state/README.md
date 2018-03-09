# Trace-State Field

Trace context is a set of common and vendor specific properties identifying the trace. `Trace-Parent` header is designed for fast parsing - it has a predefined structure and fixed length fields. `Trace-State` header carries the extended properties in a form of collection of name/value pairs.

`Trace-State` header is defined separately from `Correlation-Context`. It is designed to carry ONLY properties defined by tracing library, not user-defined properties. This way cloud vendors and libraries may guarantee it's value transmission. Transmission of a larger baggage header is not guaranteed.  

## HTTP Format
The HTTP header format is defined [here](HTTP_HEADER_FORMAT.md) and the rationale is defined [here](HTTP_HEADER_FORMAT_RATIONALE.md).

## Binary Format
TODO: add link here