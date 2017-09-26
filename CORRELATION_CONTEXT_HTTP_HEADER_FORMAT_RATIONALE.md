# Rationale for Correlation Context HTTP Header Format

This document provides rationale for the decisions made for the `Correlation-Context` header format.

## Purpose of a header

Correlation context header is used to propagate properties not defined in `Trace-Context`. There are two common use cases. First is to define a context on trace initiation. Such context will have customer's identity, high-level operation name and other properties like a flight name. Second use case is to pass the caller's name to the next component. This name-value pair will be overridden by every service to it's own name.

## General considerations

- Should be human readable. Cryptic header will hide the fact of potential information disclosure.
- Should be appende-able (comma-separated) https://tools.ietf.org/html/rfc7230#page-24 so nodes can add context properties without parsing an existing headers.
- Some systems specify type of value. Most commonly the same set as JSON allows - boolean and numeric. Should allow to express this.
- It is expected that the typical name will be a single word in latin and the value will be a short string in latin or a derivative of an url.

## Trimming of spaces

Header should be human readable and editable. Thus spaces are allowed before and after the comma separator.

## Strings encoding

Url encoding is low-overhead way to encode unicode characters for non-latin characters in the values. Url encoding keeps a single words in latin unchanged and easy readable.

## Limits

The idea behind limits is to provide trace vendors common safeguards so the content of the `Correlation-Context` header can be stored with the request. Thus the limits are defined on the number of keys, max pair length and the total size. The last limit is the most important in many scenarios as it allows to plan for the data storage limits.

Another consideration was that cookies may be an alternative way to store and pass the correlation context fields. So the limits should make context name-value pairs fit the typical cookie limit.

- *Maximum number of name-value pairs* - this limit was taken as a number of cookies allowed by Chrome.
- *Maximum number of bytes per a single name-value pair* - the limit allows to store URL as a value with some extra details as a single context name-value pair. It is also a typical cookie size limitation.
- *Maximum total length of all name-value pairs* - TODO: LOOKING FOR SUGGESTIONS HERE

