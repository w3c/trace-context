# Request Context Header Format Rationale

This document provides rationale for the decisions made for the `Request-Context` header format.

## Why not a `Correlation-Context`?

Semantic of the new header is different from `Correlation-Context`. 
- this header will not be propagated to the next component 
- there will be no information exposure (I only trust who I call)
- header can be used in both - request and response

Alternative approach of setting `ttl` on individual correlation context properties require more parsing. It also easier to mess up by libraries which do not follow the semantics.

## Header format

Format of the header should be 100% compatible with `Correlation-Context` header format for ease of maintenance.