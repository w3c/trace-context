[![Build Status](https://img.shields.io/travis/w3c/distributed-tracing/master.svg?label=validation%20service)](./test/)

# Distributed Tracing Working group

This repository is associated with the [Distributed Trace Context Working Group](https://www.w3.org/2018/distributed-tracing/).

Specification for distributed tracing context propagation format:

- Trace Context
  [Report](https://w3c.github.io/distributed-tracing/report-trace-context.html).
  Status: [First Public Working
  Draft](https://www.w3.org/2017/Process-20170301/#working-draft).
  - Rationale [document](trace_context/HTTP_HEADER_FORMAT_RATIONALE.md)
  - Changes are tracked on GitHub, communicated in meetings and e-mails
    distribution list.
- Correlation Context
  [Report](https://w3c.github.io/distributed-tracing/report-correlation-context.html).
  Status: initial draft.
  - Rationale [document](correlation_context/HTTP_HEADER_FORMAT_RATIONALE.md)
- Working group [charter](https://www.w3.org/2018/07/distributed-tracing.html) (as of working group creation). Live [charter document](https://w3c.github.io/distributed-tracing/charter.html).
- Original [community group](https://www.w3.org/community/trace-context/).

## Team Communication

Overview of team related communication channels:

- GitHub issues for any specification related issues.
- Mailing List for general discussions. Please subscribe to [public-trace-context@w3.org](http://lists.w3.org/Archives/Public/public-trace-context/).
- Gitter Channel to reach the team: [TraceContext/Lobby](https://gitter.im/TraceContext/Lobby).
- Public Google calendar for all meetings and events [Google Calendar](https://calendar.google.com/calendar?cid=ZHluYXRyYWNlLmNvbV81YTA5cWh1YTZmaDdqYjIzaDd2ZGpnNnZlZ0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t).

We appreciate feedback and contributions. Please make sure to read rationale documents when you have a question about particular
decision made in specification.

## Goal

This specification defines formats to pass trace context information across systems. Our goal is
to share this with the community so that various tracing and diagnostics products can operate
together.

## Reference Implementations

TODO: add link here

## Why are we doing this

- If this becomes popular, frameworks and other services will automatically pass trace IDs 
through for correlated requests. This would prevent traces from hitting dead ends when a request
reaches an un-instrumented service.
- Once aligned on a header name, we can ask for a CORS exception from the W3C. This would allow
browsers to attach trace IDs to requests and submit tracing data to a distributed tracing service.
- Loggers can reliably parse trace / span IDs and include them in logs for correlation purposes.
- Customers can use multiple tracing solutions (Zipkin + New Relic) at the same time and not have
 to worry about propagating two sets of context headers.
- Frameworks can *bless* access to the trace context even if they prevent access to underlying
request headers, making it available by default.

## Contributing

See [Contributing.md](CONTRIBUTING.md) for details.