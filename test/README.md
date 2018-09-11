# W3C Distributed Tracing Validation Service

## Install
* Make sure you have Python version >= 3.6.0 installed.
	```
	> python --version

	Python 3.7.0
	```
* Install aiohttp package.
	```
	> pip install aiohttp
	```

## Implement Test Service
The test harness will use HTTP POST to communicate with your test service endpoint, giving instructions via the POST body, and waiting for your service to callback to the harness.

#### HTTP POST body format
The HTTP POST request body from the harness will be a JSON array, each element in the array would be an object with two properties `url` and `arguments`. The test service should iterate through the JSON array, and for each element, send an HTTP POST to the specified `url`, with `arguments` as the request body.

Below is a sample request from the test harness:
```
POST /test HTTP/1.1
Accept: application/json
Accept-Encoding: gzip, deflate
Host: 127.0.0.1:5000
User-Agent: Python/3.7 aiohttp/3.3.2
Content-Length: 118
Content-Type: application/json

[
    {"url": url1, "arguments": [
        {"url": url2, "arguments": []}
    ]},
    {"url": url3, "arguments": []}
]
```

## Run Test Cases
* Make sure your [test service](#implement-test-service) is running.
* Run the test script against your test service endpoint (e.g. `http://127.0.0.1:5000/test`).
	```
	> python test.py http://127.0.0.1:5000/test
	```
* After the test completed, you will get the result.
	```
	harness listening on http://127.0.0.1:7777
	test_multiple_requests (__main__.AdvancedTest) ... ok
	test_both_traceparent_and_tracestate_missing (__main__.TraceContextTest) ... ok
	test_traceparent_header_name (__main__.TraceContextTest) ... ok
	test_traceparent_header_name_valid_casing (__main__.TraceContextTest) ... ok
	test_traceparent_included_tracestate_missing (__main__.TraceContextTest) ... ok
	test_traceparent_trace_flags_illegal_characters (__main__.TraceContextTest) ... FAIL

	======================================================================
	FAIL: test_traceparent_trace_flags_illegal_characters (__main__.TraceContextTest)
	----------------------------------------------------------------------
	Traceback (most recent call last):
	File "test.py", line 130, in test_traceparent_trace_flags_illegal_characters
		self.assertNotEqual(trace_id, '12345678901234567890123456789012')
	AssertionError: '12345678901234567890123456789012' == '12345678901234567890123456789012'

	----------------------------------------------------------------------
	Ran 6 tests in 0.381s

	FAILED (failures=1)
	```
* There are optional environment variables which allow you to control the harness behavior. Please read the help message from `python test.py`.
	```
	Usage: python test.py <service endpoint> [patterns]

	Environment Variables:
		HARNESS_DEBUG      when set, debug mode will be enabled (default to disabled)
		HARNESS_HOST       the public host/address of the test harness (default 127.0.0.1)
		HARNESS_PORT       the public port of the test harness (default 7777)
		HARNESS_TIMEOUT    the timeout (in seconds) used for each test case (default 5)
		HARNESS_BIND_HOST  the host/address which the test harness binds to (default to HARNESS_HOST)
		HARNESS_BIND_PORT  the port which the test harness binds to (default to HARNESS_PORT)
		SERVICE_ENDPOINT   your test service endpoint (no default value)

	Example:
		python test.py http://127.0.0.1:5000/test
		python test.py http://127.0.0.1:5000/test TraceContextTest.test_both_traceparent_and_tracestate_missing
		python test.py http://127.0.0.1:5000/test AdvancedTest
		python test.py http://127.0.0.1:5000/test AdvancedTest TraceContextTest.test_both_traceparent_and_tracestate_missing
	```
* Alternatively, you can use the Python [unit testing framework](https://docs.python.org/3/library/unittest.html) module to run the test.
	```
	> python -m unittest
	```
	To enable verbose output:
	```
	> python -m unittest -v
	```
	Instead of running all the test cases, you can pick a specific test case:
	```
	> python -m unittest test.TraceContextTest.test_traceparent_header_name
	```
* When the environment variable HARNESS_DEBUG is set (to any non-empty value), debug info will be dumped to the console output:
	```
	> python test.py http://127.0.0.1:5000/test AdvancedTest
	harness listening on http://127.0.0.1:7777
	test_multiple_requests (__main__.AdvancedTest) ...

	Harness trying to send the following request to your service http://127.0.0.1:5000/test

	POST http://127.0.0.1:5000/test HTTP/1.1
	traceparent: 00-12345678901234567890123456789012-1234567890123456-01

	[{'arguments': [],
	'url': 'http://127.0.0.1:7777/callback/608bf55129ae4e4eafef75909cc47c49.0'},
	{'arguments': [],
	'url': 'http://127.0.0.1:7777/callback/608bf55129ae4e4eafef75909cc47c49.1'},
	{'arguments': [],
	'url': 'http://127.0.0.1:7777/callback/608bf55129ae4e4eafef75909cc47c49.2'}]

	Your service http://127.0.0.1:5000/test responded with HTTP status 200


	Your service http://127.0.0.1:5000/test made the following callback to harness

	Host: 127.0.0.1:7777
	User-Agent: python-requests/2.19.1
	Accept-Encoding: gzip, deflate
	Accept: */*
	Connection: keep-alive
	Content-Length: 2
	traceparent: 00-12345678901234567890123456789012-1e3438eafec64bdf-01

	Your service http://127.0.0.1:5000/test made the following callback to harness

	Host: 127.0.0.1:7777
	User-Agent: python-requests/2.19.1
	Accept-Encoding: gzip, deflate
	Accept: */*
	Connection: keep-alive
	Content-Length: 2
	traceparent: 00-12345678901234567890123456789012-a08ab06e8541419c-01

	Your service http://127.0.0.1:5000/test made the following callback to harness

	Host: 127.0.0.1:7777
	User-Agent: python-requests/2.19.1
	Accept-Encoding: gzip, deflate
	Accept: */*
	Connection: keep-alive
	Content-Length: 2
	traceparent: 00-12345678901234567890123456789012-a50f507837844515-01


	ok

	----------------------------------------------------------------------
	Ran 1 test in 0.204s

	OK
	```