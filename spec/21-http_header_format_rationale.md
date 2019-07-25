# Trace context HTTP header format rationale

This document provides rationale for the decisions made, mapping the `traceparent` and `tracestate` fields to HTTP headers.

## Lowercase concatenated header names

While HTTP headers are conventionally delimited by hyphens, the trace context header names are not. Rather, they are lowercase concatenated `traceparent` and `tracestate` respectively. The departure from convention is due to practical concerns of propagation. Trace context is unlike typical HTTP headers, which are point-to-point and do not propagate through other systems like messaging. Different systems have different constraints. For example, some cannot read case insensitively, and others forbid the hyphen character. Even if we could suggest not using the same format for such systems, we know many systems transparently copy HTTP headers into fields. This class of concerns only exist when we choose to support mixed case with hyphens. By choosing not to, we open trace context integration beyond HTTP at the cost of a conventional distraction.

## All parts of `traceparent` are required

We've been discussing to make parts of the `traceparent` header optional. One proposal we declined was to allow trace-id-only `traceparent` headers. The intended use was to save size for small clients (like mobile devices) initiating the call. The rationale for declining it was to avoid abuse and confusion. A suggestion that we want to discuss on saving size is to use binary format.

Making `trace-flags` optional doesn't save a lot, but makes specification more complicated. And it potentially can lead to incompatible implementations which do not expect `trace-flags`.

## Span/parent nomenclature

We were using the term `span-id` in the `traceparent`, but not all tracing systems are built around span model, e.g. X-Trace, Canopy, SolarWinds, are built around event model, which is considered more expressive than the span model. There is nothing in the spec actually requires the model to be span-based, and passing the ID of the happened-before "thing" should work for both types of trace models. We considered names `call-id`, `request-id`. However out of all replacements `parent-id` is probably the best name. First, it matched the header name. Second it indicates a difference between caller and callee. Discussing AMQP we realized that `message-id` header defined by AMQP refers to individual message, and semantically not the same as traceparent. Message id can be used to dedup messages on the server when traceparent only defines the source this message came from.

## Ordering of keys in `tracestate`

The specification calls for ordering of values in tracestate. This requirement allows better interoperability between tracing vendors.

A typical <a>distributed trace</a> is clustered - components calling each other are often monitored by the same tracing vendor. So information supplied by the tracing system which originated a request will typically be less and less important deeper in a <a>distributed trace</a>. Immediate caller's information on the other hand typically is more valuable as it is more likely being monitored by the same tracing vendor. Thus, it is logical to move immediate caller's information to the beginning of the `tracestate` list. So less important values will be pushed to the end of the list.

This prioritization of `tracestate` values improves performance of querying the value of tracestate - typically you only need a first pair. It also allows you to meaningfully truncate `tracestate` when required instead of dropping the entire list of values.

## Mutations of `tracestate`

Two questions that comes up frequently is whether the `tracestate` header HAVE TO be mutated on every mutation of `parent-id` to identify the vendor which made this change and whether two different vendors can modify the `tracestate` entries in a single component.

This requirement may improve interoperability between vendors. For instance, a vendor may check the first `tracestate` key and provide some additional value for the customer by adjusting data collection in the current component via the knowledge of a caller's behavior. For instance, applying specific sampling policies or providing an experience for customers to get data from the caller's vendor. There are more scenarios that might be simplified by strict mutation requirements.

Even though improved interoperability will enable more scenarios, the specification does not restrict the number of mutations of `tracestate` and doesn't require the mutation.

The main reason for not requiring the mutation is generic tracers. Generic tracers are tracers which don't need to carry any information via `tracestate` and/or don't have a single back-end where this data will be stored. The only thing a generic tracer can set in `tracestate` is either a key with some constant, an empty value or a copy of  `traceparent`. Neither of those details is particularly interesting for the callee. But a requirement puts an extra burden and complexity on implementors. Another reason for not requiring a mutation is that allowing multiple mutations may require vendors to check for more than one key anyway.

Some back-end neutral SDKs may be implemented so that destination back-end is decided via side-car or out-of-process agent configuration. In such cases a customer may decide to enable more than one headers' mutation logic in in-process SDK. Another requirement for multiple mutations is that in a similar environment where the back-end destination is decided via out-of-process configuration - certain header mutations may still be required. An example may be smart sampling mechanisms that rely on additional data propagation in `tracestate`.

## Size limits of `tracestate`

### Total size limit

The field `tracestate` opens up rich interoperability and extensibility scenarios for vendors. There are defined use cases for the `tracestate` like positioning request in multiple distributed tracing graphs and providing backward compatibility with older protocols. But `tracestate` is not limited to this use and will drive innovations and new scenarios going forward.

The opaque nature of `tracestate` introduces some tension between guarantees to vendors around propagating vendor-specific data with traces vs. storage and propagation constraints.

On the one hand, field value should be small so implementors can satisfy the requirement to pass the value all the time. It is especially critical for various messaging systems where metadata like `tracestate` is not paid for by the customer and provided for free.

On the other hand, in order for the field to be useful there should be some guarantees that it will in fact be propagated in most of the cases.

Without changing definition of `tracestate` to make it less opaque, any declared limit will be arbitrary. It may be based on discussions with vendors on their needs. But it's still arbitrary as - first, it may not account for the needs of everybody and second - whatever guarantee will be provided - it will be abused as guaranteed propagation is a very tempting and hard to implement feature.

Talking about abuse - one thing this working group is doing is working on user-defined context propagation as part of [Correlation Context](https://w3c.github.io/correlation-context/) spec. Correlation context will provide a relieve valve for people who want to have freedom propagating relatively big payload across the components of a distributed trace.

This specification allows removing and adding as many `tracestate` entries as an implementation needs. This freedom is required to satisfy privacy and interoperability concerns. Thus all suggestions specification is making regarding the size of `tracestate` field will only be a recommendation that would improve vendors interoperability and cannot be "enforced" in practice.

Three solutions to address this problem were discussed:

1. Declare the arbitrary max length that HAVE TO be propagated.
2. Limit based on number of entries, not the size. Declare arbitrary minimum number of entries required for propagation.
3. Make max length the decision of the implementor. Suggest arbitrary max length in specification that implementors SHOULD propagate.

These solutions has the following pros and cons.

#### 1. Declare the arbitrary max length

This is simplest and easy to understand solution. Proposals for the limit varied from `20` (size of a single `parent-id` with small identifier) to `1024` to fit up to 5 vendors with large tracestate entries. `512` is a nice median length.

Extremely small proposal like `64` wasn't received well by vendors, while larger limits was unacceptable/undesirable for cloud vendors as costs of implementing it are quite high.

We failed to find a number everybody liked.

#### 2. Limit based on number of entries

This proposal was made to eliminate the problem of a "greedy" vendor utilizes the full length of a `tracestate` and ultimately blocking the interoperability.

Problem with this proposal is that limits proposed for the individual entry (e.g. `128`) were still quite high for cloud providers.

Also even though seemingly this proposal makes interoperability better, abuse of using multiple entries by a single vendor is still unavoidable.

Good way to discourage vendors to use long `tracestate` values is to suggest to remove those first when limit was reached.

#### 3. Make max length the decision of the implementor

Options above "protected" vendors from implementors who will take optional nature of `tracestate` and will not propagate `tracestate`. However the reality is that for many platforms even larger `tracestate` fields propagation is not a concern.

So there was a proposal that the spec will suggest the length limits, and define the algorithm of trimming `tracestate`. However the final decision of an actual implementation to the platform.

One of the side effects of this proposal is that it encourages tracing vendors to minimize the use of `tracestate` for non-essential scenarios to ensure propagation of an essential fields. Which is aligned with the spirit of `tracestate`.

One addition to this scenario was made to discourage people using `tracestate` values of size larger than `128` long. Specification suggests to cut those entries first.

### Maximum number of elements

Here are some rationals and assumptions:

- the total size can be calculated 2 * num_elements - 1 (delimiters) + sum(key.size()) + sum(value.size()).
- we assume that each key will have around 4 elements (e.g. `msft`, `goog`, etc).
- we assume that each value will have 8 or more characters (e.g. one hex int32).
- based on the previous two assumptions each key-value pair will have more than 12 characters.

Based on these assumptions and rationals a maximum number of elements of 32 looks like a reasonable compromise.

## Forcing lower case tracestate names

Lowercase names have a few benefits:
- consistent with structured headers specification http://httpwg.org/http-extensions/draft-ietf-httpbis-header-structure.html
- make naming consistent and avoid potential interoperability issues between systems
- encourages minimizing the name size to a single word

## String encoding of names

Url encoding is low-overhead way to encode unicode characters for non-latin characters in the values. Url encoding keeps a single words in latin unchanged and easily readable.

## Vendor name in a key

Sign `@` is allowed in a key for easy parsing of vendor name out of the tracestate key. The idea is that with the registry of tracing vendors one can easily understand the vendor name and how to parse it's trace state. Without `@` sign parsing will be more complicated. Also `@` sign has known semantics in addressing for protocols like ftp and e-mails.

## Versioning

Versioning options are:

1. Pass thru unknown headers
2. Re-start trace when you see unknown header
3. Try to parse trace following some rules when you see unknown header

One variation is whether original or new header that you cannot recognize is preserved in `tracestate`.

- Option 1 is least favorable as it makes one bad header break the entire <a>distributed trace</a>.
- Option 2 is better. It's easy, doesn't restrict future version in any way and re-started trace should be understood by new systems. So only one "connection" is lost. And the lost connection issue can be solved by storing the original header in `tracestate`. Drawbacks are also obvious. First, single old component always breaks traces. Second, it's harder to transition without customer disatisfaction of broken traces.

  Storing original value also has negative effects. Valid `traceparent` is 55 characters (out of 512 allowed for `tracestate`). And "bad" headers could be much longer pushing valuable `tracestate` pairs out. Also this requirement increases the chance of abuse. When a bad actor will start sending a header with the version `99` that is only understood by that actor. And the fact that every system passes thru the original value allows this actor to build a complete solution based on this header.
- Option 3 with the fallback to option 2 seems to allow the easiest transition between versions by forcing a lot of restrictions on the future. Initial proposal was to try to parse individual parts like `trace-id` than `parent-id`. Assuming `parent-id` size or format may change without changing `trace-id`. However the majority sees potential for abuse here. So we suggest to force future versions to be additive to the current format. And if parsing fails at any stage - simply restart the trace.

## Restarting trace

Developers sometimes feel a need to restart a trace due to security concerns, however trace context should not contain information that can compromise your application,  and tracing vendors should work through the risks of trusting incoming identifiers without compromising on interoperability.

If restarting a trace is unavoidable, you SHOULD clear the `tracestate` list as well. The data carried in `tracestate` carries information that often has a strong association with the `traceparent`, particularly `trace-id`. Tracing vendors will often assume that these values are associated, which is why `tracestate` SHOULD be cleared when `traceparent` is changed.

There are scenarios, however, which may require different behavior. For example, if a trace was restarted when entered some secure boundaries and than restored back when it is leaving those boundaries - keeping the original `tracestate` entries will fully restore the trace back to normal. In this example, vendor-specific context will be propagated through these secure boundaries.

Scenarios like the one above require careful coding and understanding of what they are trying to achieve, and should be considered an exception. Implementations should discourage this type of restarts. For example, implementations may allow this scenario only by means of restarting the trace WITH `tracestate` clean up and than re-population of `tracestate` can only be implemented as an explicit copy/pasting of `tracestate` entries one by one.

## Response headers

**TL;DR;** There are many scenarios where collaboration between distributed tracing vendors require writing and reading response headers. We can see that this can have value, but don't think right now is the right time to standardize. We decided we would rather wait for individual vendors to start to collaborate over response headers and later decide which scenarios are worth standardizing. Use of `traceparent` and `tracestate` headers is not forbidden in response headers.

### Use Cases

1. Restart a trace and return new trace identification information to caller.
2. Send Tenant ID/identity of the service so caller knows where to query telemetry from.
3. Notify upstream to sample trace sending a sampling flag (+ sampling score) for delegated sampling.
4. Report back data to the caller (like server timing, method name, application type and version). E.g. for HTTP call - caller only knows the url when server knows route information. Route information may be helpful to caller to group outgoing requests.

### Open Issues

- If standard defines response headers - are they required or optional?
- How are they propagated to the caller of the caller? Is this done via multiple hops?
- Some IoT devices may not expect relatively large response headers.

### Potential Content of a Header

- `traceparent` can be used for use cases 1 and 3 (identity and deferred sampling).
- `tracestate`-like header can be used for all use cases.

### Problems

- Might not work in all scenarios (e.g queues).
- Not sure what processing etc. would look like.
