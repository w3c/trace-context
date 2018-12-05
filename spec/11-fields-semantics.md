# Semantics of trace context

Trace context is represented by a set of name/value pairs describing the
identity of every http request. Two propagation fields `traceparent` and
`tracestate` carry the common and vendor-specific properties that make up the
trace context.

The field `traceparent` carries four properties:

1. `Trace-id` field which uniquely identifies a distributed trace.
2. `Parent-id` field identifying this call as caller knows it.
3. `Recorded` flag that provides a hint on whether information about this
   distributed trace was recorded by caller.

The field `tracestate` represents the vendor-specific list of name/value pairs.

## Relationship between the fields

The `traceparent` field represents the incoming request in a tracing system in
a common format. The `tracestate` field includes the parent in a potentially
vendor-specific format.

For example, a client traced in the congo system adds the following fields to
an outbound request (examples are given in http format).

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4
```

If the receiving server is traced in the `rojo` tracing system, it carries over
the state it received and adds a new entry with the position in its trace.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
tracestate: rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01,congo=BleGNlZWRzIHRohbCBwbGVhc3VyZS4
```

You'll notice that the `rojo` system reuses the value of `traceparent` in its
entry in `tracestate`. This means it is a generic tracing system. Otherwise,
`tracestate` entries are opaque.

If the receiving server of the above is `congo` again, it continues from its
last position, overwriting its entry with one representing the new parent.

``` http
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b9c7c989f97918e1-01
tracestate: congo=lZWRzIHRoNhcm5hbCBwbGVhc3VyZS4,rojo=00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01
```

Notice when `congo` wrote its `traceparent` entry, it reuses the last trace ID
which helps in consistency for those doing correlation. However, the value of
its entry `tracestate` is opaque and different. This is ok.

Finally, you'll see `tracestate` retains an entry for `rojo` exactly as it was,
except pushed to the right. The left-most position lets the next server know
which tracing system corresponds with `traceparent`. In this case, since `congo`
wrote `traceparent`, its `tracestate` entry should be left-most.

Detailed definitions of the field follows.

## Trace-id

Is the ID of the whole trace forest. It is represented as a 16-bytes array, for
example, `4bf92f3577b34da6a3ce929d0e0e4736`. All bytes `0` are considered
invalid.

`Trace-id` is used to uniquely identify a distributed trace. So implementation
should generate globally unique values. Many algorithms of unique identification
generation are based on some constant part - time or host based hashes and a
random value. There are systems that make random sampling decisions based on the
value of `trace-id`. So to increase interoperability it is recommended to keep
the random part on the right side of `trace-id` value.

When a system operates with a shorter `trace-id` - it is recommended to fill-in
the extra bytes with random values rather than zeroes. Let's say the system
works with a 8-byte `trace-id` like `3ce929d0e0e4736`. Instead of setting
`trace-id` value to `0000000000000003ce929d0e0e4736` it is recommended to
generate a value like `4bf92f3577b34da6a3ce929d0e0e4736` where
`4bf92f3577b34da6a` is a random value or a function of time & host value. Note,
even though a system may operate with a shorter `trace-id` for distributed trace
reporting - full `trace-id` should be propagated to conform to the
specification.

## Parent-id

Is the ID of this call as known by the caller. It is also known as `span-id` as
a few telemetry systems call the execution of a client call a span. It is
represented as an 8-byte array, for example, `00f067aa0ba902b7`. All bytes `0`
is considered invalid.

`Parent-id` should be generated as a random number to guarantee uniqueness for a
single distributed trace. Algorithms relying on incrementing the value may
result in repeating `parent-id` values sent by different components. Which will
make it harder to correlate caller and callee of the call inside a single
distributed trace.

## Recorded Flag

Many distributed tracing scenarios may be broken when only a subset of calls
participated in a distributed trace were recorded. At certain load recording
information about every incoming and outgoing request becomes prohibitively
expensive. Making a random or component-specific decision for data collection
will lead to fragmented data in every distributed trace. Thus it is typical for
tracing vendors and platforms to pass recording decision for given distributed
trace or information needed to make this decision.

There is no consensus on what is the best algorithm to make a recording
decision. Various techniques include: probability sampling (sample 1 out of 100
distributed traced by flipping a coin), delayed decision (make collection
decision based on duration or a result of a call), deferred sampling (let callee
decide whether information about this request need to be collected). There are
variations and customizations of every technique which can be tracing vendor
specific or application defined.

Field `tracestate` is designed to handle the variety of techniques for making
recording decision specific (along any other specific information) for a given
tracing system or a platform. Flag `recorded` is introduced for better
interoperability between vendors. It allows to communicate recording decision
and enable better experience for the customer.

For example, when SaaS services participate in distributed trace - this service
has no knowledge of tracing system used by its caller. But this service may
produce records of incoming requests for monitoring or troubleshooting purposes.
Flag `recorded` can be used to ensure that information about requests that were
marked for recording by caller will also be recorded by SaaS service. So caller
can troubleshoot the behavior of every recorded request.

Flag `recorded` has no restriction on its mutations except that it can only be
mutated when `parent-id` was updated. See section "Mutating the traceparent
field". However there are set of suggestions that will increase vendors
interoperability.

1. If component made definitive recording decision - this decision SHOULD be
   reflected in `recorded` flag.
2. If component needs to make a recording decision - it SHOULD respect
   `recorded` flag value. Security considerations should be applied to protect
   from abusive or malicious use of this flag - see security section.
3. If component deferred or delayed decision and only a subset of telemetry will
   be recorded - flag `recorded` should be propagated unchanged. And set to `0`
   as a default option when trace is initiated by this component. There are two
   additional options:
    1. Component that makes deferred or delayed recording decision may
       communicate priority of recording by setting `recorded` flag to `1` for a
       subset of requests.
    2. Component may also fall back to probability sampling to set flag
       `recorded` to `1` for the subset of requests.
