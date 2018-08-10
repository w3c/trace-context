# Security

There are two areas of security risk - information exposure to malicious dependency service and denial of monitoring
by malicious caller. Both risks are not new with the standard. Standard makes it more likely to get attacks uses these
headers.

## Information exposure

unintentionally propagated out to HTTP servers outside of your organization's administrative
control

sensitive information in tracestate exposure.


## Denial of monitoring by malicious caller

if you have enabled tracing on a service with a public API and naively continue any trace with
the sampling flag set using the trace ID provided, a malicious attacker (or simply any third party using the
HTTP headers) could overwhelm your application with tracing overhead, forge trace ID collisions that make your
monitoring data unusable, or run up your tracing bill with your SaaS tracing vendor.

