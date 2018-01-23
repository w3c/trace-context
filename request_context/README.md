# Request-Context Header

Request context header is used to propagate request and response properties not defined in `Trace-Context`. 
Typical use case is to pass the caller's and callee's name to the next component or return to the calling component.

## HTTP Format
The HTTP format is defined [here](HTTP_HEADER_FORMAT.md) and the rationale is defined
[here](HTTP_HEADER_RATIONALE.md).

## Binary Format
TODO: add link here