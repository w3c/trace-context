# Correlation Context Header Format Rationale

This document provides rationale for the decisions made for the `Correlation-Context` header format.

## General considerations

- Should be human readable. Cryptic header will hide the fact of potential information disclosure.
- Should be appende-able (comma-separated) https://tools.ietf.org/html/rfc7230#page-24 so nodes 
can add context properties without parsing an existing headers.
- It is expected that the typical name will be a single word in latin and the value will be a 
short string in latin or a derivative of an url.

## Why a single header?

Another option is to use prefixed headers, such as `trace-context-X` where `X` is a propagated 
field name. This could reduce the size of the data, particularly in http/2 where header 
compression can apply.

Generally speaking `Correlation-Context` header may be split into multiple headers and 
compression may be at the same ballpark as repeating values will be converted into a single value
in HPAC's dynamic collection. That's said there were no profiling made to make this decision.

The approach with multiple headers has the following problems:
- Name values limitation is much more pressing when the context name is used a part of a header 
name.
- The comma-separated format similar to the proposed still needs to be supported in every 
individual header. This makes parsing harder.
- Single header is easier to configure for tracing by many app servers.

## Why not Vary-style?

The [Vary](https://tools.ietf.org/html/rfc7231#section-7.1.4) approach is another alternative, 
which could be used to accomplish the same. For example, `Correlation-Context: x-b3-parentid;
ttl=1` could tell the propagation to look at and forward the parent ID header, but only to the 
next hop. This has an advantage of http header compression (hpack) and also weave-in with legacy 
tracing headers.

Vary approach may be implemented as a new "header reference" value type `ref`. 
`Correlation-Context: x-b3-parentid;type=ref;ttl=1` if proven needed.

## Trimming of spaces

Header should be human readable and editable. Thus spaces are allowed before and after the comma 
separator.

## Case sensitivity of names

There are few considerations why the names should be case sensitive:
- some keys may be a url query string parameters which are case sensitive
- forcing lower case will decrease readability of the names written in camel case

## Strings encoding

Url encoding is low-overhead way to encode unicode characters for non-latin characters in the 
values. Url encoding keeps a single words in latin unchanged and easy readable.

## Limits

The idea behind limits is to provide trace vendors common safeguards so the content of the 
`Correlation-Context` header can be stored with the request. Thus the limits are defined on the 
number of keys, max pair length and the total size. The last limit is the most important in many 
scenarios as it allows to plan for the data storage limits.

Another consideration was that HTTP cookies provide a similar way to pass custom data via HTTP 
headers. So the limits should make the correlation context name-value pairs fit the typical 
cookie limits.

- *Maximum number of name-value pairs* - this limit was taken as a number of cookies allowed by 
Chrome.
- *Maximum number of bytes per a single name-value pair* - the limit allows to store URL as a 
value with some extra details as a single context name-value pair. It is also a typical cookie 
size limitation.
- *Maximum total length of all name-value pairs* - TODO: LOOKING FOR SUGGESTIONS HERE

