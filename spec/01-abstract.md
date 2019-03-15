# Problem Statement

Distributed tracing is a methodology implemented by tracing tools to follow, analyze
and debug a transaction across multiple software components. Typically, a
<a>distributed trace</a> traverses more than one component which requires it to
be uniquely identifiable across all participating systems.
Trace context propagation passes along this unique identification.

Today, trace context propagation is implemented individually by each tracing vendor.
In multi-vendor environments, this causes interoperability problems, like:

- Traces that are collected by different tracing vendors cannot be linked together
  as there is no shared unique identifier.
- Traces that cross boundaries between different tracing vendors break as there
  is no uniformly agreed set of identification that is forwarded.
- Cloud platform vendors, as well as hardware vendors, cannot guarantee to support
  trace context propagation as there is no standard to follow.

In the past, these problems did not have a significant impact as most applications
were monitored by a single tracing tool and stayed within the boundaries of a single
platform provider. Today, an increasing number of applications are highly
distributed and leverage multiple middleware services and cloud platforms.

## Solution

The trace context specification defines a universally agreed-upon format for the
exchange of trace context propagation data - referred to as *trace context*. Trace
context solves the problems described above by

- providing a unique identifier for individual traces, allowing traces of multiple
  providers to be linked together.
- providing an agreed-upon mechanism to forward vendor-specific trace data and
  avoid broken traces when multiple trace tools participate in a single transaction.
- providing an industry standard that platform- and hardware-providers can support.

A unified approach for propagating trace data improves visibility into the behavior
of distributed applications, facilitating problem and performance analysis.
The interoperability provided by trace-context is a prerequisite to manage modern
micro-service based applications.
