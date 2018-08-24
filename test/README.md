# W3C Distributed Tracing Validation Service

## Install
* Make sure you have Python version >= 3.5.4 installed.
	```
	> python --version

	Python 3.7.0
	```
* Install aiohttp package.
	```
	> pip install aiohttp
	```

## Run Test Harness
* From the test folder, run the test harness:
	```
	> python harness.py
	```
	Alternatively, you can specify the binding address and port:
	```
	> python harness.py 127.0.0.1 8080
	```
	The test harness will start and output the endpoint, you can access the endpoint from a browser:
	```
	harness listening on http://127.0.0.1:8080
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

## Run Test Cases in Web Browser
* Make sure both the [test harness](#run-test-harness) and your [test service](#implement-test-service) are running.
* Open browser, navigate to the root path of test harness, which you can get from the harness console output, for example, `http://127.0.0.1:8080`.
* You will be prompted for your test endpoint, provide the endpoint which has implemented the [HTTP POST body format](#http-post-body-format), for example, `http://127.0.0.1:5000/test`.
* The test would start and you should be able to see interactive results from the browser.

#### Tips
* The test endpoint would be saved to session cookie, so you don't have to type in again next time. If you do need to switch to another test endpoint, either clear the session cookie from your browser, or start a In-Private session.
* For convenience, you can also provide the test endpoint via anchor, for example, `http://127.0.0.1:8080#http://127.0.0.1:5000/test`. This will make it easier if you want to send the link to someone else and let them run the test cases.

## Run Test Cases from Command Shell
TBD
