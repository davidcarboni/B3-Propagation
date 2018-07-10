[![Build Status](https://travis-ci.org/davidcarboni/B3-Propagation.svg?branch=master)](https://travis-ci.org/davidcarboni/B3-Propagation)

# B3 Propagation

Implements B3 propagation for Python.

Does not implement communication with a Zipkin server.

Available on Pypi: https://pypi.org/project/B3-Propagation/

## B3

B3 is used by [Zipkin](http://zipkin.io/) for building distributed trace trees.
It's the set of headers and values you need to use when doing distributed tracing.

Specifically, this implements: https://github.com/openzipkin/b3-propagation

## Purpose

The aim is to make it clean and simple to read and propagate B3 headers.

This code intentionally implements B3 only. 
It does not send tracing information to a Zipkin server.

There are two use cases:

 * You're interested in distributed log aggregation, but not interested in using Zipkin.
 * You'd like a B3 implementation to base your own Zipkin instrumentation on.

## Motivation

I built this library to enable Python to "play nicely" in a distributed tracing environment 
(specifically taking into account [Spring Cloud Sleuth](https://cloud.spring.io/spring-cloud-sleuth/)).

I want to be able to correlate logs across multiple services and
I don't need the full power of Zipkin at this stage.
This provides a relatively low-impact first-step on the distributed tracing journey.

Incoming B3 values are made available and B3 headers can be generated for onward requests.


## Usage

You'll get two things from this implementation:

 * B3 values for the current span are made available via the `values()` function. 
 These can be included in [log lines sent to stdout](https://12factor.net/logs) 
 so that log handling can be externalised, keeping services small and focused.
 * Sub-span headers can be created 
 for propagating trace IDs when making calls to downstream services.

Here are the three steps you'll need to use B3 propagation.

### Collect B3 headers from an incoming request

This could be called from, say, a Flask `before_request()` function, 
passing in, say, `request.headers`.
Alternatively, it can be directly passed to `before_request()`. 
This will generate any needed identifiers 
(e.g. a new `trace_id` for a root span):

```python
app.before_request(lambda: b3.start_span(request.headers))
```

If you want the end of a span to be logged ("Server Send")
you can call the following (or pass it directly to `Flask.after_request`):

```python
app.after_request(b3.end_span)
```

### Add headers to onward requests

If your service needs to call other services, 
you'll need to add B3 headers to the outgoing request.
This is done by starting a new sub-span, optionally passing in headers to be updated.
Once this is done, you'll get subspan IDs returned from `values()`
(e.g. for logging) until you end the subspan.
This will set up the right B3 values for a sub-span in the trace
and return a dict containing the headers you'll need for your service call:

```python
with SubSpan([headers]) as b3_headers:
    ... log.debug("Calling downstream service...")
    ... r = requests.get(<downstream service>, headers=b3_headers)
    ... log.debug("Downstream service responded...")
```

### Access B3 values 

When you need to work with tracing information, for example to build log messages, 
this gets you a dict with keys that match the B3 header names 
(`X-B3-TraceId`, `X-B3-ParentSpanId`, `X-B3-SpanId`, `X-B3-Sampled` and `X-B3-Flags`) for the current span (or subspan if you've started one): 

```python
values()
``` 

### Logging Level

By default, the `b3` logger is set to `INFO` and trace messages are logged at this level. 
Additional debugging information is logged at the `DEBUG` level. 

If you want to switch off the tracing messages then alter the log level as follows 

```python
logging.getLogger('b3').setLevel('WARNING')
```

### Change Trace/Span character length

By default, both `trace` and `span` identifiers generated will be a 16-character hexadecimal encoding of an 8-byte array, as determined by the `trace_len` and `span_len` parameters.
In some cases you may wish to change this. 
For example, the Stackdriver Trace API expects the `trace` id to be 32 characters and the `span` id to be 16, do this as follows
```
b3.trace_len = 32
```

## Other stuff

This library has no dependencies.
It's intended to be straightforward to use with Flask apps, but doesn't require Flask.
This means that if you're using a different framework, or maybe something like GRPC, you can still handle B3 headers.

This library is based on https://github.com/daidcarboni/Flask-B3 (https://pypi.org/project/Flask-B3)


## Is that it?

Surely it's more complicated, needs configuration, or does this and that else?

No. That's all. 

