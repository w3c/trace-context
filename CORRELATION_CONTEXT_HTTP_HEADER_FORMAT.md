# Correlation Context HTTP Header Format

A correlation context header is used to pass the name-value context properties (also known as tags) for the trace. This is a companion header for the `Trace-Context`. The values are intended for control of logging systems and should be passed along to any child requests. 

# Format

## Header name

`Correlation-Context`

Multiple correlation context headers are allowed. Values can be combined in a single header according to [rfc](https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2).

## Field value

`name1=value1[;type=(number|bool|string)], name2=value2[;type=(number|bool|string)]`

Overall Correlation-Context length MUST NOT exceed `1024` bytes. Key and value length should stay well under the combined limit of `1024` bytes. 

## Supported value types

### String

Default value type. Represents a url encoded string value

**Examples**:

```
component=Frontend
component=Frontend;type=string
component=Front%3Dend
```

### Boolean

Binary flag. Supported values `true` and `false`

**Examples**:

```
IsAuthenticated=true;type=bool
IsAuthenticated=false;type=bool
```

### Number

Numeric value in invariant culture (`.` as a decimal separator).

**Examples**:

```
ExposurePercentage=33.33;type=number
Step=10;type=number
```

# Examples of HTTP headers

```
Correlation-Context: component=Frontend, flightName=DF:28, IsAuthenticated=true;type=bool
```

```
Correlation-Context: component=Frontend
Correlation-Context: flightName=DF:28, ExposurePercentage=33.33;type=number
```
