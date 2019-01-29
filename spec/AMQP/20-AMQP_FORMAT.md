# AMQP format

The Advanced Message Queuing Protocol (AMQP) is an open internet protocol for
business messaging. It defines a binary wire-level protocol that allows for the
reliable exchange of business messages between two parties. AMQP can be used as
a protocol for asynchronous communication between components of an application.
From the distributed tracing and telemetry correlation perspective it is a
known problem to be able to correlate a component that placed message and
component that processed it later. This specification describes how trace
context MUST be encoded into AMQP messages.

## Trace context fields placement in a message

AMQP defines message as a payload with the additional annotations sections.
There are two annotation sections this specification refers -
"application-properties" and "message-annotations". See
[3.2](http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-messaging-v1.0-os.html#section-message-format)
of *OASIS Advanced Message Queuing Protocol (AMQP) Version 1.0, Part 3:
Messaging* (AMQP specification).

AMQP message section "application-properties" is immutable collection of
properties that is defined by message publisher and can be read by the message
consumer. Message brokers cannot mutate those properties. Section
"message-annotations" is designed for message brokers to use and can be mutated
during the message processing.

Fields `traceparent` and `tracestate` SHOULD be added to the message in the
application-properties section by message publisher. Once the message has been
created, it’s no longer permissible to edit the bare message. So if it were
necessary to annotate the message inside the middleware as it transits, that
MUST happen in the “message-annotations” section, using the
“application-properties” as a base. Message reader SHOULD construct the full
trace context by reading `traceparent` and `tracestate` fields from the
“message-annotations” first and if not exist - from “application-properties”.

## Trace context and failed read/write operations

This specification defines how to propagate context from publisher thru broker
to ultimate reader. It does not define any additional transport level correlation
constructs that can be used to investigate failed publish or read operations.

It is recommended, however, for AMQP implementations to make the best effort
attempt to read the trace context from the message and use it while reporting
such problems.

TODO: do we need to define a way to specify trace context of read operation? Is
there anything in AMQP protocol that can be used to carry this context?

## `traceparent` AMQP format

The field `traceparent` MUST be encoded and decoded using [binary
protocol](..\extension-binary.html) and stored as a binary type defined in
section
[1.6.19](http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-types-v1.0-os.html#type-binary)
of AMQP specification.

Property name MUST be `traceparent` - all lowercase without delimiters.

## `tracestate` AMQP format

The field `tracestate` MUST be encoded and decoded as a string to string map.
See definition of type map in section
[1.6.23](http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-types-v1.0-os.html#type-map)
of AMQP specification.

---

*NOTE about the strings encoding*

Please note that strings are defined as UTF-8 in AMQP. Should anything be
different from the HTTP encoded opaque strings? Should we allow to benefit from
wider character set for better encoding of opaque values? Or this will be too
error prone?

---

Property name MUST be `tracestate` - all lowercase without delimiters.

## Relations with message id field

The field `message-id` is defined in section
[3.2.4](http://docs.oasis-open.org/amqp/core/v1.0/amqp-core-messaging-v1.0.html#type-properties)
of AMQP specification.

Message-id, if set, uniquely identifies a message within the message system. The
message producer is usually responsible for setting the message-id in such a way
that it is assured to be globally unique. A broker MAY discard a message as a
duplicate if the value of the message-id matches that of a previously received
message sent to the same node.

Trace context identifies the context of a worker who either publish or read the
message while message-id identifies the content of the message. So the message
with the same message-id can be send twice with the different values of trace
context fields in case of retries. Also trace context can be changed from broker
to broker to identify the broker while message-id will not be changed.

It is recommended to use a unique `parent-id` for every publish of a message. So
it is not possible that `traceparent` will be identical for the messages with
the different `message-id`.

## AMQP specific security and privacy considerations

AMQP defines a protocol for a potentially long living messages. Long-term
storing of `traceparent` and `tracestate` fields may require additional handling
of security and privacy as that may not be covered by "in-flight" data
exemptions.

So all the same privacy and security techniques should be applied with the
potentially more strict requirements.

## Size sensitive environments

TODO: There are many good reason to keep the format and sizes of fields
unchanged. For the size-sensitive environments, if you ONLY INITIATE the message
outside of existing context – there may be a possibility to save on size by
truncating or reusing some fields.

## Batching

The specification defines a binding to the AMQP "message format 0", i.e. the
layout that is defined in the Messaging section of the the AMQP spec, but does
not provide any further detail on HOW those messages are being transferred.

AMQP is enormously efficient when filling link credit with sending messages in
sequence without any special overlaid batching. And is often used without
batching.

Message brokers like Azure Service Bus, Azure Event Hub and others have a
special message format that can batch multiple AMQP messages into one. However
the way to bind to that format is by specifying a binding to the individual
messages and then have the proprietary batching model pick that up via the
binding to the standard message.