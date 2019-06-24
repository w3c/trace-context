# Security Considerations

There are two types of potential security risks associated with this specification: information exposure and denial of service attacks against the tracing system.

Services and platforms relying on `traceparent` and `tracestate` headers should also follow all the best practices of parsing potentially malicious headers. Including checking for header length and content of header values. These practices help to avoid buffer overflow and html injection attacks.

## Information exposure

As mentioned in the privacy section, information in `traceparent` and `tracestate` headers may carry information that can be considered sensitive. For example, `traceparent` may allow one call to be correlated to the data sent with another call. `tracestate` may imply the version of monitoring software used by the caller. This information could potentially be used to create a larger attack.

Application owners should either ensure that no proprietary or confidential information is stored in the `tracestate`, or they should ensure that `tracestate` isn't present in requests to external systems.

## Denial of service

When distributed tracing is enabled on a service with a public API and naively continues any trace with the `sampled` flag set, a malicious attacker could overwhelm an application with tracing overhead, forge `trace-id` collisions that make monitoring data unusable, or run up your tracing bill with your SaaS tracing vendor.

Tracing vendors and platforms should account for these situations and make sure that checks and balances are in place to protect denial of monitoring by malicious or badly authored callers.

One examples of such protection may be different tracing behavior for authenticated and unauthenticated requests. Various rate limiters for data recording can also be implemented.

## Other risks

Application owners need to make sure to test all code paths leading to the sending of `traceparent` and `tracestate` headers. For example, in single page browser applications it is typical to make cross-origin calls. If one of these code path leads to the sending of `traceparent` and `tracestate` headers - cross-origin calls restricted via <a data-cite='FETCH#http-access-control-request-headers'>`Access-Control-Allow-Headers`</a> [[FETCH]], it may fail.
