# Rationale for AMQP protocol decisions

## Strings vs. complex types

Complex types in most cases cheaper than string representation of `traceparent`
and `tracestate`. It is important in size restricted environments like IoT and
price-sensitive infrastructures where one pays for message metadata stored in a
queue server for a long time.

Complex types are well defined and widely used in AMQP and they are part of a
protocol. So using them is fully supported by all existing clients.

## Binary `traceparent` vs. list of binary values

There are multiple ways to implement a `traceparent`. It can either be
implemented as string (http-like), binary protocol (like for grpc) or list of
separate binary values (`trace-id`, `parent-id`, `trace-flags`).

Strings duplicating the size of a field, using list of binaries will require to
redefine the way the field serialized, parsed, and versioned. So re-using binary
protocol looks like a logical solution.

## AMQP map for `tracestate`

The benefit of using a built-in map type for AMQP is that serialization and
de-serialization of the field is built in and doesn't require any custom
implementation for parsing it.

Maps in AMQP preserving the order so there is no conflict with the semantics of
the field.

## Why use both - application and message properties

Trace context is defined in an app in a context that mostly operates with the
application-properties collection. So ideally trace context should be set and
carried as part of application-properties collection. However,
application-properties are immutable so there should be a fallback mechanism to
use message-annotations if tracing must be implemented by one of message
brokers.

## Why not delivery-annotations

There are three grand scenarios:

*Application trace context* through a simple AMQP brokered entity. If you send a
message into a queue from an app and then pull that message from the queue with
the same or another app and nothing else interesting happens,
application-properties is the right place, because you're not doing any tracing
of the broker, you're just passing the context alongside the message.

*Application context plus routing context*. If you have a chain of AMQP entities
as you might have in a complex routing scenario, you might want to enrich the
context as the message is being passed on. In that case, the prior scenario
still exists, i.e. you will still want the option to have the context
information as set by the message producer and use that for application level
tracing unencumbered by whatever the routing layer might be tracking. As the
routing layer gets it hand on the message for tracing, it basically forks the
context off into the message-annotations and that's being manipulated on the
route. As the message reaches the destination, you now have the app-level
context from the producer in the application-properties AND the routing context
that was layered on top of that in the message-annotations.

Hop to hop tracing: A delivery-annotations usage scenario would be purely
additive to either of the prior two, allowing any intermediary to spawn a new
context for itself or to propagate a context only via subset of hops. I think
that is fairly esoteric at this point and we should NOT take that into a spec
unless someone shows a hard use-case.

## Prefix of the field names

The properties are typically prefixed because they’re generic and might
interfere with an app’s use of the same names. So, for instance, instead of
`traceparent` prefixed name like `w3c:traceparent` can be used. In general AMQP
apps tend to be more metadata heavy than HTTP. For instance, `http:` is used in
the HTTP-over-AMQP spec.

The question is whether prefix is required for trace context and if so - what
may be the name of the prefix. Options may be `w3c` for the origin of the spec,
`tcx` for trace context, `dt` for distributed tracing.

However in the current spec, even if customer decided to use the same name, the
chance that customer didn’t mean to override those properties intentionally is
very small. Those are rare names. So prefix doesn’t add much, but increases a
chance for an error and interoperability.

So suggestion is to keep the name un-prefixed.