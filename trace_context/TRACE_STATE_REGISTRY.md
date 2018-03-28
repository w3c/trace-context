# Trace State Registry
Each tracestate entry is a position within a trace. A trace can span multiple tracing systems, compatibly given common formats. The below registry of well-known labels allow participating parties to map a format to a tracestate entry. For example, the "b3" format includes a concatenation of data previously represented by headers prefixed with X-B3-.

This registry serves a secondary purpose, which is to reserve words for well-known public services. For example, the label "aws" might imply both a format and also a single trace namespace.

| Trace State Name | Vendor / Project Name | website | Format |
| - | :-: | - | - |
| sw | Apache SkyWalking (Incubating) | http://skywalking.io/ | [SkyWalking Propagation Headers](https://github.com/apache/incubator-skywalking/blob/master/docs/en/Skywalking-Cross-Process-Propagation-Headers-Protocol-v1.md) |

The registry rows should be in alphabeta order of **Trace State Name**.
