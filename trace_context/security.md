# Security

There are two areas of security risk specific to this specification - information exposure to malicious
dependency service and denial of monitoring by malicious caller. Both risks exist with modern approaches
for distributed trace context propagation. Having a standard for context propagation provides attackers
with a known way of triggering tracing within an application. It makes more likely for a service to
receive these attacks.

Services and platforms relying on `traceparent` and `tracestate` headers should also follow all the
best practices of parsing potentially malicious headers. Including checking for headers length and content of headers
values. These practices help to avoid buffer overflow and html injection attacks.

## Information exposure

As mentioned in privacy section, information in `traceparent` and `tracestate` headers may carry information that can be
considered as sensitive. For example, `traceparent` may allow to correlate calls so identify from one call may be correlated
to the data sent with another call. `tracestate` may imply the version of monitored software used by caller. This
information can be used to author an attack to the service.

Application owners should either ensure that no proprietary or confidential information is stored into the `tracestate`, or
they should ensure that `tracestate` isn't present in requests to external systems.

## Denial of monitoring by malicious caller

When distributed tracing is enabled on a service with a public API and naively continues any trace with
the sampling flag set, a malicious attacker could overwhelm an application with tracing overhead, forge trace ID collisions
that make monitoring data unusable, or run up your tracing bill with your SaaS tracing vendor.

Tracing vendors and platforms should account to these situations and make sure that checks and balances are in place to
protect denial of monitoring by malicious or badly authored callers.

## Other risks

Application owners need to make sure to test all code path leading to sending of `traceparent` and `tracestate` headers. For
example, browsers single page applications it is typical to make cross-origin calls from the browser. If one of code paths leads
to sending of `traceparent` and `tracestate` headers - cross-origin calls restricted via `Access-Control-Allow-Headers` [header](https://www.w3.org/TR/cors/#access-control-allow-headers-response-header) may fail.
