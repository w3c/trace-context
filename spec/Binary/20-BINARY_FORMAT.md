# Binary format

Binary format document describes how to encode each field - `traceparent` and
`tracestate`. The binary format should be used to encode the values of these
fields. This specification does not specify how these fields should be stored
and send as a part of a binary payload. The basic implementation may serialize
those as size of the field followed by the value.

# `Traceparent` binary format

The field `traceparent` encodes the version of the protocol and fields
`trace-id`, `parent-id` and `recorded`. Each field starts with the one byte
field identifier with the field value following immediately after it. Field
identifiers are used as markers for additional verification of the value
consistency and may be used in future for the versioning of the `traceparent`
field.

``` abnf
traceparent     = version version_format  
version         = 1BYTE                   ; version is 0 in the current spec
version_format  = "{ 0x0 }" trace-id "{ 0x1 }" parent-id "{ 0x2 }" recorded
trace-id        = 16BYTES
parent-id       = 8BYTES
trace-flags     = 1BYTE  ; only the least significant bit is used
```

Unknown field identifier (anything beyond `0`, `1` and `2`) should be treated as
invalid `traceparent`. All zeroes in `trace-id` and `parent-id` invalidates the
`traceparent` as well.

## Serialization of `traceparent`

Implementation SHOULD serialize fields into the field ordering sequence. In
other words, `trace-id` field should be serialized first, `parent-id` second and
`trace-flags` - third.

Field identifiers should be treated as unsigned byte numbers and should be
encoded in big-endian bit order.

When `trace-id` is represented as a byte array - first element of an array MUST
be copied first. When array is represented as a memory block of 16 bytes -
serialization of `trace-id` would be identical to `memcpy` method call on that
memory block. Same applies to `parent-id` field.

If padding of the field is required (`traceparent` needs to be serialized into
the bigger buffer) - any number of bytes can be appended to the end of the
serialized value.

## De-serialization of `traceparent`

Let's assume the algorithm takes a buffer and can set and shift cursor in the
buffer as well as validate whether the end of the buffer was reached or will be
reached after reading the given number of bytes. De-serialization of
`traceparent` should be done in the following sequence:

1. If buffer is empty - return invalid status `BUFFER_EMPTY`. Set a cursor to
   the first byte.
2. Read the `version` byte at the cursor position. Shift cursor to `1` byte.
3. If all three fields (`trace-id`, `parent-id`, `trace-flags`) already read -
   return them with the status `OK` if `version` is `0` or status
   `DOWNGRADED_TO_ZERO` otherwise.
4. If at the end of the buffer return invalid status `TRACEPARENT_INCOMPLETE`.
   Otherwise read the field identifier byte at the cursor position. Field
   identifier should be read as unsigned byte assuming big-endian bits order.
    1. If `0` - check that remaining buffer size is more or equal to `16` bytes.
       If shorter - return invalid status `TRACE_ID_TOO_SHORT`. Otherwise read
       the next `16` bytes for `trace-id` and shift cursor to the end of those
       `16` bytes. Go to step `3`. If `trace-id` is represented as a byte array
       - first byte should be set into the first element of that array. See
         comment in serialization section.
    2. If `1` - check that remaining buffer size is more or equal to `8` bytes.
       If shorter - return invalid status `PARENT_ID_TOO_SHORT`. Otherwise read
       the next `8` bytes for `parent-id` and shift cursor to the end of those
       `8` bytes. Go to step `3`.
    3. If `2` - check the remaining size of the buffer. If at the end of the
       buffer - return invalid status. Otherwise - read the `trace-flags`
       byte. Least significant bit will represent `recorded` value. Go to step
       `3`.
    4. In case of any other value - if `version` read at step `2` is `0` -
       return invalid status `INVALID_FIELD_ID`. If `version` has any other
       value - `INCOMPATIBLE_VERSION`.

_Note_, that invalid status names are given for readability and not part of the
specification.

_Note_, that parsing should not treat any additional bytes in the end of the
buffer as an invalid status. Those fields can be added for padding purposes.
Optionally implementation can check that the buffer is longer than `29` bytes as
a very first step if this check is not expensive.

## `traceparent` example

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