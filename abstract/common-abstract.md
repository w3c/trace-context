Distributed tracing is a set of tools and practices to monitor the health and reliability of a distributed application. Distributed application is an application that consists of multiple components deployed and operated separately. It is also known as micro-service. 

The main concept of a distributed tracing is telemetry correlation. Telemetry correlation is a way to correlate events from one component to the events from another. It allows to find the cause-effect relationship for these events. For instance – find which user action in browser caused the failure in business logic layer. 

To correlate events between components, these components need to exchange a piece of information called trace context. Typically trace context consist of originating event identifier, originating component identity and some user-defined properties. 

Unifying the format of trace context propagation as well as aligning on semantical meaning of the values is the main objective of this community group. The goal is to share this with the community so that various tracing and diagnostics products can operate together. 
