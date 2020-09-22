# Use Cases for response Headers

The [Response Header Specification](https://github.com/w3c/trace-context/blob/master/spec/21-http_response_header_format.md) defines the format for response headers.

As response headers solve (largely) different use cases, this doc aims to collect them and also address possible implications, like privacy issues.

This document is a loose, unordered and ongoing collection.

## Usecase 1: Report the proposed parent ID back to the caller 

A system, like a browser, can not create a trace ID and span ID.
The callee could generate the parent ID and then send it back to the caller via response header.
This parent ID would represent the parent of the spans created by the callee.
