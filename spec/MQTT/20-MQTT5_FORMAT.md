# MQTT 5 format

MQTT is a messaging protocol. As any messaging protocol it is commonly used as a
mechanism for asynchronous or postponed execution of tasks. In those scenarios
publisher of the message needs to communicate the trace context of execution to
the consumer of that same message. So publishing and consuming tasks can be
analyzed as a part of a single distributed trace.

## Trace context fields placement in a message

Starting v5.0 MQTT defines a message as a payload with the associated [User
Properties](http://docs.oasis-open.org/mqtt/mqtt/v5.0/cos01/mqtt-v5.0-cos01.html#_Toc514847989).
User properties MUST be used to propagate trace context and MUST follow the
following convention.

## Field `traceparent`

Field `traceparent` MUST be set in user properties under the name `traceparent`.
All lower case, no delimiters. Value of the `traceparent` field MUST follow the
[main specification](index.html) format. Example of `traceparent` field value:

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
```

## Field `tracestate`

Field `tracestate` MUST be set in user properties under the name `tracestate`.
All lower case, no delimiters. Value of the `tracestate` field MUST follow the
[main specification](index.html) format - comma delimited list of name-value
pairs. Example of `tracestate` field value:

``` http
tracestate: congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4,rojo=00f067aa0ba902b7
```