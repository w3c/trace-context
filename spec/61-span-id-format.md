## Considerations for `span-id` field generation

This section suggests some practices to consider when implementing
`span-id` generation algorithms to ensure
interoperability between different systems.

### Uniqueness of `span-id`

The value of `span-id` SHOULD be unique within a <a>distributed trace</a>.
If the value of `span-id` is not unique within a distributed trace,
parent-child relationships between spans within the distributed trace
may be ambiguous.

### Randomness of `span-id`

Values of `span-id` SHOULD be randomly generated. Randomness of `span-id`
addresses some [security](#security-considerations) and [privacy
concerns](#privacy-considerations) of exposing unwanted information.
Randomness also ensures a high probability, though not a guarantee, of
uniqueness within a distributed trace.
