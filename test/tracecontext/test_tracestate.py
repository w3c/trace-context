import unittest
from tracecontext import Tracestate

class TestTracestate(unittest.TestCase):
	def test_ctor_no_arg(self):
		state = Tracestate()
		self.assertEqual(state.to_string(), '')

	def test_ctor_with_dict(self):
		state = Tracestate({'foo': '1'})
		self.assertEqual(state.to_string(), 'foo=1')

	def test_ctor_kwargs(self):
		state = Tracestate(foo = '1', bar = '2', baz = '3')
		self.assertEqual(state.to_string(), 'foo=1,bar=2,baz=3')

	def test_ctor_with_string(self):
		state = Tracestate('foo=1,bar=2,baz=3')
		self.assertEqual(state.to_string(), 'foo=1,bar=2,baz=3')

		self.assertRaises(ValueError, lambda: Tracestate('foobarbaz'))

	def test_cctor(self):
		state = Tracestate(Tracestate('foo=1,bar=2,baz=3'))
		self.assertEqual(state.to_string(), 'foo=1,bar=2,baz=3')

	def test_all_allowed_chars(self):
		header = ''.join([
			# key
			''.join(map(chr, range(0x61, 0x7A + 1))), # lcalpha
			'0123456789', # DIGIT
			'_',
			'-',
			'*',
			'/',
			# "="
			'=',
			# value
			''.join(map(chr, range(0x20, 0x2B + 1))),
			''.join(map(chr, range(0x2D, 0x3C + 1))),
			''.join(map(chr, range(0x3E, 0x7E + 1))),
		])
		state = Tracestate(header)
		self.assertEqual(state.to_string(), header)

	def test_delimiter(self):
		state = Tracestate('foo=1, \t bar=2')
		self.assertEqual(state.to_string(), 'foo=1,bar=2')

		state = Tracestate('foo=1,\t \tbar=2')
		self.assertEqual(state.to_string(), 'foo=1,bar=2')

	def test_getitem(self):
		state = Tracestate({'foo': '1'})
		self.assertEqual(state['foo'], '1')

	def test_method_from_string(self):
		state = Tracestate()
		state.from_string('foo=1')
		state.from_string('bar=2')
		state.from_string('baz=3')
		self.assertEqual(state.to_string(), 'foo=1,bar=2,baz=3')

		# test load order
		state = Tracestate()
		state.from_string('baz=3')
		state.from_string('bar=2')
		state.from_string('foo=1')
		self.assertNotEqual(state.to_string(), 'foo=1,bar=2,baz=3')

	def test_method_is_valid(self):
		state = Tracestate()

		# empty state not allowed
		self.assertFalse(state.is_valid())

		state['foo'] = 'x' * 256
		self.assertTrue(state.is_valid())

		# exceeds 512 bytes
		state['bar'] = 'x' * 256
		self.assertFalse(state.is_valid())
		self.assertTrue(Tracestate(state.to_string()[:512]).is_valid())
		self.assertFalse(Tracestate(state.to_string()[:513]).is_valid())

	def test_method_repr(self):
		state = Tracestate('foo=1, bar=2, baz=3')
		self.assertEqual(repr(state), "Tracestate('foo=1,bar=2,baz=3')")

	def test_pop(self):
		state = Tracestate('foo=1,bar=2,baz=3')
		self.assertEqual(state.pop(), ('baz', '3'))
		self.assertEqual(state.to_string(), 'foo=1,bar=2')
		self.assertEqual(state.pop(), ('bar', '2'))
		self.assertEqual(state.to_string(), 'foo=1')
		self.assertEqual(state.pop(), ('foo', '1'))
		self.assertEqual(state.to_string(), '')
		# raise KeyError exception while trying to pop from nothing
		self.assertRaises(KeyError, lambda: state.pop())

	def test_setitem(self):
		state = Tracestate(bar = '0')
		state['foo'] = '1'
		state['bar'] = '2'
		state['baz'] = '3'
		self.assertEqual(state.to_string(), 'baz=3,bar=2,foo=1')

		# key SHOULD be string
		self.assertRaises(ValueError, lambda: state.__setitem__(123, 'abc'))
		# value SHOULD NOT be empty string
		self.assertRaises(ValueError, lambda: state.__setitem__('', 'abc'))
		# key SHOULD NOT have uppercase
		self.assertRaises(ValueError, lambda: state.__setitem__('FOO', 'abc'))

		# key with vendor format
		state['special@vendor'] = 'abracadabra'
		self.assertRaises(ValueError, lambda: state.__setitem__('special@', 'abracadabra'))
		self.assertRaises(ValueError, lambda: state.__setitem__('@vendor', 'abracadabra'))

		# value SHOULD be string
		self.assertRaises(ValueError, lambda: state.__setitem__('FOO', 123))
		# value SHOULD NOT be empty string
		self.assertRaises(ValueError, lambda: state.__setitem__('foo', ''))
		# value SHOULD NOT contain invalid character
		self.assertRaises(ValueError, lambda: state.__setitem__('foo', 'bar=baz'))

		state['foo'] = 'x' * 256
		# throw if value exceeds 256 bytes
		self.assertRaises(ValueError, lambda: state.__setitem__('foo', 'x' * 257))

if __name__ == '__main__':
	unittest.main()
