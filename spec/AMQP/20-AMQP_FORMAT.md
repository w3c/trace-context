# AMQP format

The AMQP binding will define for traceparent and tracestate to be added to the
message in the application-properties section (as “w3c:tracestate” and
“w3c:traceparent”) if they are added by the original message publisher. Once the
message has been created, it’s no longer permissible to edit the bare message,
so if it were necessary to annotate the message inside the middleware as it
transits, that will happen in the “message-annotations” section, using the
“application-properties” as a base. The ultimate receiver can then pick between
the full context including infrastructure and the pure app context by either
looking into “message-annotations” or “application-properties”.
 
1. *Protocol justification*. I suggest just reference W3C specs as they did in cloud events. And keep names of “headers”.
2. *Size-sensitive environments*. There is a good reason to keep the format and sizes unchanged. For the size-sensitive environments
If you ONLY INITIATE the message outside of existing context – there may be a possibility to save on size by truncating fields.
Discuss how to use binary protocol instead of textual.
Differences with message-id. Discuss how message-id is a deduplication concept where Trace-Context identifies the context of worker who either put or read the message.
Batching of messages – recommended semantics of TraceContext fields when batching is happening.


Failed post or get – what is relationship between failed operation trace
   context and message trace context.
Log entire app properties to get correlation.

Mutation of trace context by queue provider – should we allow/recommend to mutate trace context fields by trace provider. Especially for the span-id.
   Security/privacy consideration – we can refer to W3C spec again. And adjust
   it if needed.

application properties is "unmodifiable" so "message-annotations" overrides
those in application

traceparent 1.6.22 (list of binary) or binary - make rationale
tracestate 1.6.23 (map of string/string type)