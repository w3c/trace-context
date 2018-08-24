W3C = {};

W3C.test = function(name, payload, callback) {
	QUnit.test(name, function(assert) {
		var scope = String(Math.floor(Math.random() * 2147483647));
		var request = payload(id => { return window.location.protocol + '//' + window.location.host + window.location.pathname + 'callback/' + scope + '.' + id; });
		var done = assert.async();
		fetch('/test/' + scope, {
			method: 'POST',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(request)
		}).then(response => {
			assert.ok(response.ok, 'HTTP response status ' + response.statusText);
			if (!response.ok) {
				done();
			}
			return response.json();
		}).then(response => {
			assert.ok(true, 'request body is ' + JSON.stringify(request));
			assert.ok(true, 'reponse body is ' + JSON.stringify(response));
			callback(id => { return response[id ? scope + '.' + id : scope]; }, assert);
			done();
		});
	});
};

W3C.get_traceparent = function(headers, assert) {
	var traceparents = [];
	headers.forEach(kv => {
		var name = kv[0];
		var value = kv[1];
		if (name.match(/^traceparent$/i)) {
			traceparents.push(value);
		}
	});
	assert.equal(traceparents.length, 1, 'expect 1 traceparent from the header, got ' + JSON.stringify(traceparents));
	var match = traceparents[0].match(/^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$/);
	match = match && {
		version: match[1],
		trace_id: match[2],
		span_id: match[3],
		trace_flags: match[4]
	};
	assert.ok(match, 'parse traceparent ' + JSON.stringify(match));
	return match;
};

W3C.get_tracestates = function(headers, assert) {
	var tracestates = [];
	headers.forEach(kv => {
		var name = kv[0];
		var value = kv[1];
		if (name.match(/^tracestate$/i)) {
			tracestates.push(value);
		}
	});
	assert.ok(true, 'got tracestate from header ' + JSON.stringify(tracestates));
	return tracestates;
};

W3C.test_single_request = function(name, url, headers, callback) {
	W3C.test(name, function(scope) {
		return [
			{url: url, headers: headers, arguments: [{url: scope('1'), arguments: []}]}
		];
	}, function(scope, assert) {
		var traceparent = W3C.get_traceparent(scope('1').headers, assert);
		var tracestates = W3C.get_tracestates(scope('1').headers, assert);
		callback(traceparent, tracestates, assert);
	});
};
