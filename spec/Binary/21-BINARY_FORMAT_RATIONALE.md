# Rationale for decision on binary format

Binary format is basically a proto-like encoding without any reference on
protobuf project.

## How can we add new fields

If we follow the rules that we always append the new ids at the end of the
buffer we can add up to 127. After that we can either use varint encoding or
just reserve 255 as a continuation byte.

## How can we remove a field

We can stop sending any field at any moment and the decoders will be able to
skip the missing ids and use the default values.
