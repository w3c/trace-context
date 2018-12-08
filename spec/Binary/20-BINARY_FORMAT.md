# Binary format

Binary format document describes how to encode each field - `traceparent` and
`tracestate`. The binary format should be used to encode the values of these
fields. This specification does not specify how these fields should be stored
and send as a part of a binary payload. The basic implementation may serialize
those as size of the field followed by the value.

# `Traceparent` binary format

The field `traceparent` encodes the version of the protocol and fields
`trace-id`, `span-id` and `recorded`. Each field starts with the one byte field
identifier with the field value following immediately after it. Field
identifiers are used as markers for additional verification of the value
consistency and may be used in future for the versioning of the `traceparent`
field.

``` abnf
traceparent     = version version_format
version_format  = "{ 0x0 }" trace-id "{ 0x1 }" parent-id "{ 0x2 }" recorded
trace-id        = 16BYTES
parent-id       = 8BYTES
trace-flags   = 1BYTE   ; only the least significant bit is counted
```

Unknown field identifier (anything beyond `0`, `1` and `2`) should be treated as
invalid `traceparent`. All zeroes in `trace-id` and `parent-id` invalidates the
`traceparent` as well.

## `Traceparent` example

``` js
{0,
  0, 75, 249, 47, 53, 119, 179, 77, 166, 163, 206, 146, 157, 0, 14, 71, 54,
  1, 52, 240, 103, 170, 11, 169, 2, 183,
  2, 1}
```

This corresponds to:

- `trace-id` is
  `{75, 249, 47, 53, 119, 179, 77, 166, 163, 206, 146, 157, 0, 14, 71, 54}` or
  `4bf9273577b34da6a3ce929d000e4736`.
- `span-id` is `{52, 240, 103, 170, 11, 169, 2, 183}` or `34f067aa0ba902b7`.
- `trace-flags` is `1` with the meaning `recorded` is true.

## `tracestate` binary format

List of up to 32 name-value pairs. Each list member starts with the 1 byte field
identifier `0`. The format of list member is a single byte key length followed
by the key value and single byte value length followed by the encoded value.
Strings are transmitted in ASCII encoding.

``` abnf
tracestate      = list-member 0*31( list-member )
list-member     = "0" key-len key value-len value
key-len         = 1BYTE ; length of the key string
value-len       = 1BYTE ; length of the value string
```

Zero length key (`key-len == 0`) indicates the end of the `tracestate`. So when
`tracestate` should be serialized into the buffer that is longer than it
requires - `{ 0, 0 }` (field id `0` and key-len `0`) will indicate the end of
the `tracestate`.