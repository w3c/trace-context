# Security

There are two areas of security risk - information exposure to malicious dependency service and denial of monitoring
by malicious caller. Both risks exist with modern approaches for distributed trace context propagation. Standard makes
it more likely for services to get these attacks.

## Information exposure

As mentioned in privacy section, information in `traceparent` and `tracestate` headers may carry information that can be
considered as sensitive. For example, `traceparent` may allow to correlate calls so identify from one call may be correlated
to the data sent with another call. `tracestate` may imply the version of monitored software used by caller. This
information can be used to author an attack to the service.

Even though the risk is minimal, application owner should make sure to control the boundary of organization's administrative
control. Tracing vendors and platforms should allow to control any unintentional propagation of distributed tracing context.

## Denial of monitoring by malicious caller

When distributed tracing was enabled on a service with a public API and naively continue any trace with
the sampling flag set using the `trace-id` provided via `traceparent` field, a malicious attacker could overwhelm an
application with tracing overhead, forge trace ID collisions that make monitoring data unusable, or run up your tracing
bill with your SaaS tracing vendor.

Tracing vendors and platforms should account to these situations and make sure that checks and balances are in place to
protect denial of monitoring by malicious or badly-authored callers.