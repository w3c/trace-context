# Trace context

The [trace context](overview.md) positions an incoming request in potentially multiple trace
graphs. For example, an incoming request might have information about its
gateway in one service, and information from its direct upstream in another.

Two propagation fields carry the common and vendor-specific properties that
make up the trace context.

* `traceparent` describes the position of the incoming request in its trace graph in a portable, fixed-length format. Its design focuses on fast parsing.

* `tracestate` maps all graphs the incoming parent is a part of in potentially vendor-specific formats. For example, if a request crosses tracing systems, there will be one entry in `tracestate` for each system.

Notably, the `tracestate` field is unreliant on data in the `traceparent`.

## Relationship to `Correlation-Context`

The trace context fields are separate from to the `Correlation-Context`, and
carry ONLY properties defined by tracing systems, not user-defined properties.
This way, cloud vendors and libraries may guarantee trace context transmission
even if it cannot transmit large user-defined properties.

## HTTP format
The HTTP header format is defined [here](HTTP_HEADER_FORMAT.md) and the rationale is defined [here](HTTP_HEADER_FORMAT_RATIONALE.md).

## Binary format
TODO: add link here