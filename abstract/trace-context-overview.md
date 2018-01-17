# Overview

Trace context represented by set of name/value pairs describing identity of every http request. As a performance optimization measure few of these pairs were promoted to a separate header. This header has fixed length and defined sequence of fields.

Libraries and platforms MUST propagate `Trace-Context` and `Trace-Context-Ext` headers to guarantee that trace will not be broken. `Correlation-Context` header is a companion header representing user-defined baggage associated with the trace. Libraries and platforms MAY propagate this header.

**TODO:** Add details on behavior when one of the headers cannot be parsed
