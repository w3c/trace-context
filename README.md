[![Build
Status](https://img.shields.io/travis/w3c/trace-context/master.svg?label=validation%20service)](https://travis-ci.com/w3c/trace-context/)

# Trace Context Specification

This repository is associated with the [Trace
Context](https://www.w3.org/TR/trace-context/) specification,
which specifies a distributed tracing context propagation format.

[Trace Context v1](https://www.w3.org/TR/trace-context-1/) has [W3C Recommendation](https://www.w3.org/2019/Process-20190301/#rec-publication) status.

The next version of specification is being developed in this repository.

The current draft of the Trace Context Specification from this repository's master branch is published to  https://w3c.github.io/trace-context/.
Explanations and justification for decisions made in this specification are written down in the [Rationale document](http_header_format_rationale.md).

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
