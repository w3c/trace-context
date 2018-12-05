# Other protocols

Trace Context propagation is crucial to enable distributed tracing scenarios
for applications spans multiple components. Http is one of the communication
protocols used for cross components correlation. Extensions of this
specification define the format of trace context serialization and
deserialization for other protocols. Note, that those extensions may be at a
different maturity level than this specification.

- [AMQP](https://w3c.github.io/trace-context/extension-amqp.html).
- [Binary](https://w3c.github.io/trace-context/extension-binary.html).