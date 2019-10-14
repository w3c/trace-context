# Implementations of Trace Context

This page contains an alphabetical list of projects and vendors that currently implement Trace Context.

## Elastic

**Website:** [https://elastic.co/products/apm](https://elastic.co/products/apm)

**Implementations:**
[Node.js](https://github.com/elastic/node-traceparent).

## Dynatrace
**Website:** [dynatrace.com](https://www.dynatrace.com)

**Implementations:**
[All technologies supported by Dynatrace OneAgent](https://www.dynatrace.com/news/blog/distributed-tracing-with-w3c-trace-context-for-improved-end-to-end-visibility-eap/).

## LightStep
**Website:** [lightstep.com](https://lightstep.com)

**Implementations:**
[Go](https://github.com/lightstep/tracecontext.go)

## OpenCensus
**Website:** [opencensus.io](https://opencensus.io)

**Implementations:**
[C#](https://github.com/census-instrumentation/opencensus-csharp/blob/4a8ddf6727eafda97a06c7c30d8a4fc2ec8b8e2f/src/OpenCensus/Trace/Propagation/TraceContextFormat.cs),
[Erlang](https://github.com/census-instrumentation/opencensus-erlang/blob/b3ab781b060b15a3cacbf43717c3aeb0c90c4a08/src/oc_propagation_http_tracecontext.erl),
[Go](https://github.com/census-instrumentation/opencensus-go/blob/ae11cd04b7789fa938bb4f0e696fd6bd76463fa4/plugin/ochttp/propagation/tracecontext/propagation.go),
[Java](https://github.com/census-instrumentation/opencensus-java/blob/e5e9d9224a1c9c5ee981981cf29e86662aef08c6/impl_core/src/main/java/io/opencensus/implcore/trace/propagation/TraceContextFormat.java),
[Node.js](https://github.com/census-instrumentation/opencensus-node/blob/fa97a9b6f19b97e1038ffa9e1be4b407f3844df2/packages/opencensus-propagation-tracecontext/src/tracecontext-format.ts),
[Python](https://github.com/census-instrumentation/opencensus-python/blob/2aef803e4a786fe0ffb14b168a8458283ccd72a0/opencensus/trace/propagation/trace_context_http_header_format.py),
[Ruby](https://github.com/census-instrumentation/opencensus-ruby/blob/8cb9771b218e440e825c99981ea405d40f735926/lib/opencensus/trace/formatters/trace_context.rb)

## OpenTelemetry
**Website:** [opentelemetry.io](https://opentelemetry.io)

**Implementations:**
[Python](https://github.com/open-telemetry/opentelemetry-python/blob/dbb3be802bae8e4e5c36748869dbc789e50de217/opentelemetry-api/src/opentelemetry/trace/__init__.py),
[Go](https://github.com/open-telemetry/opentelemetry-go/blob/3362421c9b41feb586ab003857894d470be57169/plugin/httptrace/httptrace.go),
[Ruby](https://github.com/open-telemetry/opentelemetry-ruby/blob/741ca61a934b05ecbaedffa56a830dc1821ca9a1/api/lib/opentelemetry/distributed_context/propagation/trace_parent.rb),
[JavaScript](https://github.com/open-telemetry/opentelemetry-js/blob/a49e7abdab3e313ad2b50a9445a885b3fd0d4783/packages/opentelemetry-core/src/context/propagation/HttpTraceContext.ts),
[Java](https://github.com/open-telemetry/opentelemetry-java/blob/63109827ea3ceba7aa099d1d0a612741a887dbac/api/src/main/java/io/opentelemetry/trace/propagation/HttpTraceContext.java)
