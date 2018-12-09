# Overview

Trace context is split into two individual propagation fields supporting interoperability and vendor-specifc extensability:

- `traceparent` describes the position of the incoming request in its trace graph in a portable, fixed-length format. Its design focuses on fast parsing. Every tracing tool MUST properly set `tracestate` even when it only relies on vendor-specif informaiton in `tracestate`
- `tracestate` extends `traceparent` with vendor-specific data represented by a set of name/value pairs. Storing information in `tracestate` is optional.

Tracing tools can provide two levels of compliant behaviour interacting with trace context:

- At a minimum they MUST propagate the `traceparent` and `tracestate` headers and guarantee  traces are not broken. this behaviour is also referred to as forwarding a trace.
- In addition they CAN also choose to participat in a trace by modifying the `traceparent` header and relevant parts of the `tracestate` header containing their proprietray information. This is also referred to as participating in a trace.

A tracing tool can choose to change this behavior for each individual request to a component it is monitoring. The decision on whether to participate or forward a trace is called sampling. A request is considered when the tracing tool participates in the trace.
