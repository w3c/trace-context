# Structured IDs 

The [Main Specification](./HTTP_HEADER_FORMAT.md) defines one way of discriminating a particular request with
a trace (the 16 hexadecimal character Span-id).   Other logging systems us a multi-level mechanism that encodes
a list of IDs that represent a particular request.   The format for this mechanism is described here.  
The following section is logically part of the 'HTTP Header Field value' section of the main specification.  

### The Structured ID Value (tag '.')

The '.' character indicates that a variable number of characters follow and represent
a structured (path based) id.   It has the form of a list of hexadecimal numbers 
(lower case) separated by '.' characters.   The list is optionally terminated by 
a '!' character.   The id ends if either the string ends or a character that 
is not a hexadecimal character or a '.' or '!' is encountered.   

Examples

```
	.1
	.3.b.34.ca25.56
	.334.ba34.93a4.1.1!
```
The structured ID is meant to represent series of causal requests within the scope
of a given Trace-id.   This whole string, like the Span-ID, identifies the request within
the context of the Trace-id.  However unlike the Span-ID this ID has structure, where 
each compoent (between the '.'s) an element in the chain of causality. For example the Trace-Context
value of 
```
*4bf92f3577b34da6a3ce929d0e0e4736.3.b.34
```
Represents a request with ID
```
*4bf92f3577b34da6a3ce929d0e0e4736.3.b.34
```
that was caused by a request with ID
```
*4bf92f3577b34da6a3ce929d0e0e4736.3.b
```
which in turn was caused by request with 
```
*4bf92f3577b34da6a3ce929d0e0e4736.3
```
Structured ID are conceptually unbounded in length, but as a practical matter must be
limited, if only to avoid issues when infinite request loops form.   The '!' character 
is meant to indicate the ID has been truncated.  The ID as a whole should still be unique
within the context of the Trace-id, but the fine grained causality information will be incomplete 
(all that is know about the last component is that it is a subchild (not the direct child) of 
the previous component).
