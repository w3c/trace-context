# Overview

Trace context consists of a set of properties crucial for event correlation in distributed applications. Trace context positions requests in a <a>distributed trace</a>. If you look at a <a>distributed trace<a> as a graph of correlated requests - a single request can be part of multiple graphs. For example, let's say component `A` calls component `B` which in turn calls `C`. One distributed tracing system may see component `A` calling component `B`. Another may see all three components communicating. So the call from `B` to `C` will carry trace context about service `A` as well as information about its direct communication upstream to `B`.

The situation when a single request is a part of multiple graphs is becoming more common. One distributed application may have components monitored by different distributed tracing systems. Those distributed tracing systems may not be easily replaceable as they might be provided by cloud vendors or distributed as pre-built components.

The trace context is designed to allow extensibility for all distributed tracing systems. It requires them to respect context set by other systems.

Trace context is represented by a set of name/value pairs describing the identity of every http request. Two propagation fields carry the common and vendor-specific properties that make up the trace context.

* `traceparent` describes the position of the incoming request in its trace graph in a portable, fixed-length format. Its design focuses on fast parsing.
* `tracestate` maps all graphs the incoming parent is a part of in potentially vendor-specific formats. For example, if a request crosses tracing systems, there will be one entry in `tracestate` for each system.

Notably, the `tracestate` field is unreliant on data in the `traceparent`.

Libraries and platforms MUST propagate `traceparent` and `tracestate` headers to guarantee that trace will not be broken.
