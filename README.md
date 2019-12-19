[![Build
Status](https://img.shields.io/travis/w3c/trace-context/master.svg?label=validation%20service)](./test/)

# Trace Context Specification

This repository is associated with the [Trace
Context](https://w3c.github.io/trace-context/) specification.

Specification for distributed tracing context propagation format:

- Trace Context [Report](https://w3c.github.io/trace-context/).
Status: [Candidate Recommendation](https://www.w3.org/Consortium/Process#candidate-rec).
  - Rationale [document](spec/21-http_header_format_rationale.md)
  - Changes are tracked on GitHub, communicated in meetings and e-mails
    distribution list.

## Team Communication

See
[communication](https://github.com/w3c/distributed-tracing-wg#team-communication)

We appreciate feedback and contributions. Please make sure to read rationale
documents when you have a question about particular decision made in
specification.

## Goal

This specification defines formats to pass trace context information across
systems. Our goal is to share this with the community so that various tracing
and diagnostics products can operate together.

## Reference Implementations

There are few open source implementations of this trace context specification
available.

A simplistic regex-based implementation can be found in the `test` folder. This
implementation has 100% compliance to the test suite.

[OpenTelemetry](https://opentelemetry.io) has alpha implementations for the following
languages:

1. [.NET](https://github.com/open-telemetry/opentelemetry-dotnet/blob/605760cf5ae0511b94d475a754f5ca1a5ec35f41/src/OpenTelemetry.Api/Context/Propagation/TraceContextFormat.cs)
2. [Go](https://github.com/open-telemetry/opentelemetry-go/blob/15bfc5bb12a4e0a02b1b96b701fd2881cefe1158/propagation/http_trace_context_propagator.go)
3. [JavaScript](https://github.com/open-telemetry/opentelemetry-js/blob/4f48357b7d1dea246a67ef1a0e071fc64aa10e26/packages/opentelemetry-core/src/context/propagation/HttpTraceContext.ts)
4. [Java](https://github.com/open-telemetry/opentelemetry-java/blob/0b21928db5085fe3deff6dfd8d28bd49dcde9e71/api/src/main/java/io/opentelemetry/trace/propagation/HttpTraceContext.java)
5. [Python](https://github.com/open-telemetry/opentelemetry-python/blob/602d42a45f6a4684342b298c5a7c4dab680e301a/opentelemetry-api/src/opentelemetry/context/propagation/tracecontexthttptextformat.py)
6. [Ruby](https://github.com/open-telemetry/opentelemetry-ruby/blob/bd6baeebb2fe65ed22e9ad33920387ce0ee8870f/api/lib/opentelemetry/distributed_context/propagation/trace_parent.rb)

Open Telemetry implementations are in active development for C++, Erlang, and PHP. In addition, [Open Census](https://opencensus.io) has an implementation for [Erlang](https://github.com/census-instrumentation/opencensus-erlang/blob/b3ab781b060b15a3cacbf43717c3aeb0c90c4a08/src/oc_propagation_http_tracecontext.erl).

.NET Framework will ship trace context specification support in the upcoming
version. See
[Activity](https://github.com/dotnet/corefx/blob/master/src/System.Diagnostics.DiagnosticSource/src/System/Diagnostics/Activity.cs)
for implementation details.

Elastic has [node.js
implementation](https://github.com/elastic/node-traceparent).

LightStep has [Go implementation](https://github.com/lightstep/tracecontext.go).

## Why are we doing this

See [Why](https://github.com/w3c/distributed-tracing-wg#why-are-we-doing-this)

## Contributing

See [Contributing.md](CONTRIBUTING.md) for details.
