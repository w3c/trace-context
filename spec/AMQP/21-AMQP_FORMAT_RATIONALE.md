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