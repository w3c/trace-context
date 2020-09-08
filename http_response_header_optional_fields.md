This document describes a set of rules which may be used to determine which optional fields to include in the HTTP response header.

## Uses of fields

Here is a quick summary of the fields available and their suggested uses.

### Version

Ensure header is parsed correctly. Always required if the header is included in the response.

### Trace ID

When called by a third party, this may be used to communicate the recorded trace ID to the caller for support purposes.

When called by a load balancer or web browser, this maybe be used to provide a trace ID to the caller so they may participate in the trace.

### Proposed Parent Id

When called by a load balancer or web browser, this maybe be used to provide a span ID to the caller so they may participate in the trace.

### Trace Flags

When called by a third party, this may be used to communicate information about the trace such as the sampled status for support purposes.

When called by a load balancer, this may be used to communicated information such as the sampled status so that the caller may intelligently decide to record its part of the trace or not.

## Suggested decision model

Of course, the header itself and all fields (except version) are always optional. If a service provider wishes not to return the response header for any reason, they are not obligated to do so. The following rules are only a recommended set of rules to encourage interoperation between tracing providers.

### Default behavior

#### Incoming call with traceparent

If the trace ID of the traceparent is used, do not include the header in the response.

If a new trace ID is used (trace restarted), include the version and the trace ID in the response.

#### Incoming call without traceparent 

Return version, trace ID, and trace flags.

### When configured as an internal server-to-server service with no load balancer (or a load balancer which does not participate in the trace).

Do not include response headers. The trace can be successful with use of only the request headers.

### When configured as an internal server-to-server service behind a tracing load balancer

Include version and trace flags in the response so the caller may respect the called service's sampling decision.

### When configured as a web server

_On initial document load only (index.html)_, include version, trace ID, proposed parent ID, and trace flags. If a web browser participates in the trace, it may use the trace ID as its own trace ID, and the proposed parent id as its own span ID.

## Known Problems

There is currently no API available to JavaScript in the browser which would allow a tracing agent to access the response header. An API would need to be implemented which allows access to the full header, or its parsed values. Alternatively, the web browser could include traceparent request headers on requests (possibly configurable by some HTML meta tag or other mechanism). This would remove the need for the response header in the browser use-case.

Operating "modes" will need to be configured by the application owner or operator.

The web browser proposed parent use case would require tracing providers to be resilient to missing root spans in the case that the first 'hop' generates a proposed span id, but the browser for some reason does not report a span with that id.