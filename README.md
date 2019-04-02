[![Build Status](https://img.shields.io/travis/w3c/trace-context/master.svg?label=validation%20service)](./test/)

# Trace Context Specification

This repository is associated with the [Trace Context](https://w3c.github.io/trace-context/) specification.

Specification for distributed tracing context propagation format:

- Trace Context
  [Report](https://w3c.github.io/trace-context/).
  Status: [Working Draft](https://www.w3.org/Consortium/Process#working-draft).
  - Rationale [document](spec/21-HTTP_HEADER_FORMAT_RATIONALE.md)
  - Changes are tracked on GitHub, communicated in meetings and e-mails
    distribution list.

## Team Communication

See [communication](https://github.com/w3c/distributed-tracing-wg#team-communication)

We appreciate feedback and contributions. Please make sure to read rationale documents when you have a question about particular
decision made in specification.

## Goal

This specification defines formats to pass trace context information across systems. Our goal is
to share this with the community so that various tracing and diagnostics products can operate
together.

## Reference Implementations

There are few open source implementations of this trace context specification
available.

A simplistic regex-based implementation can be found in the `test` folder. This
implementation has 100% compliance to the test suite.

[Open Census](https://opencensus.io) has implementations for the following
languages:

1. [C#](https://github.com/census-instrumentation/opencensus-csharp/blob/4a8ddf6727eafda97a06c7c30d8a4fc2ec8b8e2f/src/OpenCensus/Trace/Propagation/TraceContextFormat.cs)
2. [Erlang](https://github.com/census-instrumentation/opencensus-erlang/blob/b3ab781b060b15a3cacbf43717c3aeb0c90c4a08/src/oc_propagation_http_tracecontext.erl)
3. [Go](https://github.com/census-instrumentation/opencensus-go/blob/ae11cd04b7789fa938bb4f0e696fd6bd76463fa4/plugin/ochttp/propagation/tracecontext/propagation.go)
4. [Java](https://github.com/census-instrumentation/opencensus-java/blob/e5e9d9224a1c9c5ee981981cf29e86662aef08c6/impl_core/src/main/java/io/opencensus/implcore/trace/propagation/TraceContextFormat.java)
5. [Node.js](https://github.com/census-instrumentation/opencensus-node/blob/fa97a9b6f19b97e1038ffa9e1be4b407f3844df2/packages/opencensus-propagation-tracecontext/src/tracecontext-format.ts)
6. [Python](https://github.com/census-instrumentation/opencensus-python/blob/2aef803e4a786fe0ffb14b168a8458283ccd72a0/opencensus/trace/propagation/trace_context_http_header_format.py)
7. [Ruby](https://github.com/census-instrumentation/opencensus-ruby/blob/8cb9771b218e440e825c99981ea405d40f735926/lib/opencensus/trace/formatters/trace_context.rb)

.NET Framework will ship trace context specification support in the upcoming
version. See
[Activity](https://github.com/dotnet/corefx/blob/master/src/System.Diagnostics.DiagnosticSource/src/System/Diagnostics/Activity.cs)
for implementation details.

Elastic has [node.js implementation](https://github.com/elastic/node-traceparent).

LightStep has [Go implementation](https://github.com/lightstep/tracecontext.go).

## Why are we doing this

See [Why](https://github.com/w3c/distributed-tracing-wg#why-are-we-doing-this)

## Contributing

See [Contributing.md](CONTRIBUTING.md) for details.
