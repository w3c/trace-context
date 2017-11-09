#  Trace Context Extended HTTP Header Format Rationale

This document provides rationale for the decisions made for the `Trace-Context-Ext` header format.

## General considerations

- Should be human readable. Cryptic header will hide the fact of potential information disclosure.
- Should be appende-able (comma-separated) https://tools.ietf.org/html/rfc7230#page-24 so nodes 
can add context properties without parsing an existing headers.
- It is expected that the typical name will be a single word in latin and the value will be a 
short string in latin or a derivative of an url.

## Size limits

Header should be small so providers can satisfy the requirement to pass the value all the time.

512 bytes looks like a reasonable compromise.

TODO: put more thoughts into it

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
