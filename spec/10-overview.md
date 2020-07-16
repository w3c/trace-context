# Overview

## Problem Statement

Distributed tracing is a methodology implemented by tracing tools to follow, analyze and debug a transaction across multiple software components. Typically, a <a>distributed trace</a> traverses more than one component which requires it to be uniquely identifiable across all participating systems. Trace context propagation passes along this unique identification. Today, trace context propagation is implemented individually by each tracing vendor. In multi-vendor environments, this causes interoperability problems, like:

- Traces that are collected by different tracing vendors cannot be correlated as there is no shared unique identifier.
- Traces that cross boundaries between different tracing vendors can not be propagated as there is no uniformly agreed set of identification that is forwarded.
- Vendor specific metadata might be dropped by intermediaries.
- Cloud platform vendors, intermediaries and service providers, cannot guarantee to support trace context propagation as there is no standard to follow.

In the past, these problems did not have a significant impact as most applications were monitored by a single tracing vendor and stayed within the boundaries of a single platform provider. Today, an increasing number of applications are highly distributed and leverage multiple middleware services and cloud platforms.

This transformation of modern applications calls for a distributed tracing context propagation standard.

## Solution

The trace context specification defines a universally agreed-upon format for the exchange of trace context propagation data - referred to as *trace context*. Trace context solves the problems described above by

- providing a unique identifier for individual traces and requests, allowing trace data of multiple providers to be linked together.
- providing an agreed-upon mechanism to forward vendor-specific trace data and avoid broken traces when multiple tracing tools participate in a single transaction.
- providing an industry standard that intermediaries, platforms, and hardware providers can support.

A unified approach for propagating trace data improves visibility into the behavior of distributed applications, facilitating problem and performance analysis. The interoperability provided by trace context is a prerequisite to manage modern micro-service based applications.

## Design Overview

Trace context is split into two individual propagation fields supporting interoperability and vendor-specific extensibility:

- `traceparent` describes the position of the incoming request in its trace graph in a portable, fixed-length format. Its design focuses on fast parsing. Every tracing tool MUST properly set `traceparent` even when it only relies on vendor-specific information in `tracestate`
- `tracestate` extends `traceparent` with vendor-specific data represented by a set of name/value pairs. Storing information in `tracestate` is optional.

Tracing tools can provide two levels of compliant behavior interacting with trace context:

- At a minimum they MUST propagate the `traceparent` and `tracestate` headers and guarantee traces are not broken. This behavior is also referred to as forwarding a trace.
- In addition they CAN also choose to participate in a trace by modifying the `traceparent` header and relevant parts of the `tracestate` header containing their proprietary information. This is also referred to as participating in a trace.

A tracing tool can choose to change this behavior for each individual request to a component it is monitoring.
