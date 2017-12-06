# Correlation-Context Header

Correlation context header is used to propagate properties not defined in `Trace-Context`. There 
are two common use cases. First is to define a context on trace initiation. Such context will 
have customer's identity, high-level operation name and other properties like a flight name. 
Second use case is to pass the caller's name to the next component. This name-value pair will be 
overridden by every service to it's own name.

## HTTP Format
The HTTP format is defined [here](HTTP_HEADER_FORMAT.md) and the rationale is defined
[here](HTTP_HEADER_FORMAT_RATIONALE.md).

## Binary Format
TODO: add link here