# Trace Context

The trace context positions an incoming request in potentially multiple trace
graphs. For example, an incoming request might have information about its
gateway in one service, and information from its direct upstream in another.

Two propagation fields carry the common and vendor-specific properties that
make up the trace context.

* `Trace-Parent` describes the position of the incoming request in its trace graph in a portable, fixed-length format. Its design focuses on fast parsing.

* `Trace-State` maps all graphs the incoming parent is a part of in potentially vendor-specific formats. For example, if an ancestor of this request was in a different trace, there will be a separate entry for the last position it was in that trace graph.

Notably, the `Trace-State` field is unreliant on data in the `Trace-Parent`,
except if the direct upstream is fully described by `Trace-Parent`.

## Relationship to `Correlation-Context`

The trace context fields are separate from to the `Correlation-Context`, and
carry ONLY properties defined by tracing systems, not user-defined properties.
This way, cloud vendors and libraries may guarantee trace context transmission
even if it cannot transmit large user-defined properties.

## HTTP Format
The HTTP header format is defined [here](HTTP_HEADER_FORMAT.md) and the rationale is defined [here](HTTP_HEADER_FORMAT_RATIONALE.md).

## Binary Format
TODO: add link here