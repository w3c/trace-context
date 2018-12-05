# Binary format

Binary format document describes how to encode each field - `traceparent` and
`tracestate`.

# `Traceparent` binary format

The field `traceparent` encodes the version of the protocol and fields
`trace-id`, `span-id` and `recorded`. Each field starts with the one byte field
identifier with the field value following immediately after it. Field
identifiers are used as markers for additional verification of the value
consistency and may be used in future for the versioning of the `traceparent`
field.

``` abnf
traceparent     = version "0" trace-id "1" parent-id "2" recorded
trace-id        = 16BYTES
parent-id       = 8BYTES
trace-options   = 1BYTE   ; only the least significant bit is counted
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

- `traceId` is
  `{75, 249, 47, 53, 119, 179, 77, 166, 163, 206, 146, 157, 0, 14, 71, 54}` or
  `4bf9273577b34da6a3ce929d000e4736`.
- `spanId` is `{52, 240, 103, 170, 11, 169, 2, 183}` or `34f067aa0ba902b7`.
- `traceOptions` is `1` with the meaning `recorded` is true.

## `tracestate` binary format

List of up to 32 name-value pairs. Each list member starts with the 1 byte field
identifier `0`. The format of list member is a single byte key length followed
by the key value and single byte value length followed by the encoded value.

``` abnf
tracestate      = list-member 0*31( list-member )
list-member     = "0" key-len key value-len value
key-len         = 1BYTE ; length of the key string
value-len       = 1BYTE ; length of the value string
```
