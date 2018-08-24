W3C.test('harness self check', function(scope) {
	return [{'url': scope('1'), 'arguments': []}];
}, function(scope, assert) {
	assert.ok(scope(), 'harness is running');
	assert.ok(scope().arguments instanceof Array, 'arguments is Array');
	assert.equal(scope().arguments.length, 1, 'arguments.length is one');
	assert.ok(scope('1'), 'harness has collected the right scope result');
});

W3C.test('test vendor service is running', function(scope) {
	return [{'url': SERVICE_ENDPOINT, 'arguments': []}];
}, function(scope, assert) {
	assert.ok(scope(), 'vendor service is running');
});

W3C.test_single_request('test both traceparent and tracestate are missing', SERVICE_ENDPOINT, [
], function(traceparent, tracestates, assert) {
});

W3C.test_single_request('test traceparent exists while tracestate missing', SERVICE_ENDPOINT, [
	['traceparent', '00-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.equal(traceparent.trace_id, '12345678901234567890123456789012', 'the existing trace_id was inherited');
	assert.notEqual(traceparent.span_id, '1234567890123456', 'a new span_id has been created');
});

W3C.test_single_request('test traceparent missing while tracestate exists', SERVICE_ENDPOINT, [
	['tracestate', 'foo=bar']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test both traceparent and tracestate exist', SERVICE_ENDPOINT, [
	['traceparent', '00-12345678901234567890123456789012-1234567890123456-01'],
	['tracestate', 'foo=bar']
], function(traceparent, tracestates, assert) {
	assert.equal(traceparent.trace_id, '12345678901234567890123456789012', 'the existing trace_id was inherited');
	assert.notEqual(traceparent.span_id, '1234567890123456', 'a new span_id has been created');
	assert.notEqual(tracestates.length, 0, 'tracestate exists');
});

W3C.test_single_request('test traceparent wrong name - trace.parent', SERVICE_ENDPOINT, [
	['trace.parent', '00-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent wrong name - trace-parent', SERVICE_ENDPOINT, [
	['trace-parent', '00-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent header name - TraceParent', SERVICE_ENDPOINT, [
	['TraceParent', '00-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.equal(traceparent.trace_id, '12345678901234567890123456789012', 'the existing trace_id was inherited');
});

W3C.test_single_request('test traceparent header name - TrAcEpArEnT', SERVICE_ENDPOINT, [
	['TrAcEpArEnT', '00-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.equal(traceparent.trace_id, '12345678901234567890123456789012', 'the existing trace_id was inherited');
});

W3C.test_single_request('test traceparent header name - TRACEPARENT', SERVICE_ENDPOINT, [
	['TRACEPARENT', '00-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.equal(traceparent.trace_id, '12345678901234567890123456789012', 'the existing trace_id was inherited');
});

W3C.test_single_request('test traceparent version - 255 (0xff)', SERVICE_ENDPOINT, [
	['traceparent', 'ff-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent version - too short', SERVICE_ENDPOINT, [
	['traceparent', '0-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent version - too long', SERVICE_ENDPOINT, [
	['traceparent', '000-12345678901234567890123456789012-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent trace_id - all zero', SERVICE_ENDPOINT, [
	['traceparent', '00-00000000000000000000000000000000-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '00000000000000000000000000000000', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent trace_id - too short', SERVICE_ENDPOINT, [
	['traceparent', '00-1234567890123456789012345678901-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '1234567890123456789012345678901', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent trace_id - too long', SERVICE_ENDPOINT, [
	['traceparent', '00-123456789012345678901234567890123-1234567890123456-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '123456789012345678901234567890123', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent span_id - all zero', SERVICE_ENDPOINT, [
	['traceparent', '00-12345678901234567890123456789012-0000000000000000-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent span_id - too short', SERVICE_ENDPOINT, [
	['traceparent', '00-12345678901234567890123456789012-123456789012345-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test_single_request('test traceparent span_id - too long', SERVICE_ENDPOINT, [
	['traceparent', '00-12345678901234567890123456789012-12345678901234567-01']
], function(traceparent, tracestates, assert) {
	assert.notEqual(traceparent.trace_id, '12345678901234567890123456789012', 'a new trace_id has been created');
});

W3C.test('test multiple calls have different trace_id', function(scope) {
	return [
		{'url': SERVICE_ENDPOINT, 'arguments': [{'url': scope('1'), 'arguments': []}]},
		{'url': SERVICE_ENDPOINT, 'arguments': [{'url': scope('2'), 'arguments': []}]},
	];
}, function(scope, assert) {
	var traceparent1 = W3C.get_traceparent(scope('1').headers, assert);
	var traceparent2 = W3C.get_traceparent(scope('2').headers, assert);
	assert.notEqual(traceparent1.trace_id, traceparent2.trace_id, 'two invocations have different trace_id');
});
