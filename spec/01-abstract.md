## Problem Statement

Distributed tracing is a methodology implemented by tracing tools enabling to follow, analyze and debug a transaction across multiple software components. Typically, a transaction passes more than one component which requires a transaction to be uniquely identified across all software components. Passing along this unique identification is referred to as context propagation.

Today context propagation is implemented in proprietary formats individually by each tracing tool provider. This results in siginficant interoperability problems between tracing tools than manifest in two major ways:

- Traces that are collected by two tracing providers cannot be linked together as there is no unique identifier linking the individual pieces together. 
- Traces are broken each time they are passed between components monitored by different tracing as there is no uniformly agree set of identifcation taht is forwarded.

In the past this problem did not have significant impact as most applications where under monitored by a single tracing tool. Today, an increasing number of applications are hgihly highly-distributed and leverage an increasing number of cloud platform and middleware services. Most of these services come with their own tracing capababilities which results in big interoperabiity problems and lack of visibility for developers and appliation operators.

## Solution

The trace context specification defines a universally agreed format for the exchange of context propagation data - referred to as trace context. Trace context solved the problems described above by

- providing a unique identifier for individual tracing allowing traces of multiple providers being linked together and 
- providing an agreed-upon mechanism to forward vendor-specific trace data avoid broken tracing when multiple trace tools particpate in a single transaction. 

Providing a unified approach for managing trace data massively increases visibility into the behaviour of distributed applications supporting problem and performance analysis. The  interoperability provided by trace-context is a prerequisite to manage modern micro-service based applications. 
