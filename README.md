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

There are few open source and commercial implementations of this trace context specification
available.

A simplistic regex-based implementation can be found in the `test` folder. This
implementation has 100% compliance to the test suite.

.NET Framework will ship trace context specification support in the upcoming
version. See
[Activity](https://github.com/dotnet/corefx/blob/master/src/System.Diagnostics.DiagnosticSource/src/System/Diagnostics/Activity.cs)
for implementation details.

A list of all currently implementations can be found [here](./implementations.md).

## Why are we doing this

See [Why](https://github.com/w3c/distributed-tracing-wg#why-are-we-doing-this)

## Contributing

See [Contributing.md](CONTRIBUTING.md) for details.
