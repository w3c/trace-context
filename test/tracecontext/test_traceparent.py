import unittest
from tracecontext import BaseTraceparent, Traceparent

class BaseTraceparentTest(unittest.TestCase):
	def test_ctor_default(self):
		traceparent = BaseTraceparent()
		self.assertEqual(traceparent.version, 0)
		self.assertEqual(traceparent.trace_id, b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
		self.assertEqual(traceparent.parent_id, b'\0\0\0\0\0\0\0\0')
		self.assertEqual(traceparent.trace_flags, 0)

	def test_ctor(self):
		self.assertRaises(ValueError, lambda: BaseTraceparent(version = 0xff))

	def test_ctor_with_variadic_arguments(self):
		traceparent = BaseTraceparent(0, None, None, 0, 'foo', 'bar', 'baz')

	def test_version_limit(self):
		traceparent = BaseTraceparent(version = 0)
		self.assertEqual(traceparent.version, 0)

		traceparent = BaseTraceparent(version = 254)
		self.assertEqual(traceparent.version, 254)

		self.assertRaises(ValueError, lambda: BaseTraceparent(version = -1))
		self.assertRaises(ValueError, lambda: BaseTraceparent(version = 255))

	def test_trace_id_limit(self):
		traceparent = BaseTraceparent(trace_id = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
		self.assertEqual(traceparent.trace_id, b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')

		self.assertRaises(ValueError, lambda: BaseTraceparent(trace_id = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'))
		self.assertRaises(ValueError, lambda: BaseTraceparent(trace_id = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'))

	def test_parent_id_limit(self):
		traceparent = BaseTraceparent(parent_id = b'\0\0\0\0\0\0\0\0')
		self.assertEqual(traceparent.parent_id, b'\0\0\0\0\0\0\0\0')

		self.assertRaises(ValueError, lambda: BaseTraceparent(parent_id = b'\0\0\0\0\0\0\0'))
		self.assertRaises(ValueError, lambda: BaseTraceparent(parent_id = b'\0\0\0\0\0\0\0\0\0'))

	def test_trace_flags_limit(self):
		traceparent = BaseTraceparent(trace_flags = 0)
		self.assertEqual(traceparent.trace_flags, 0)

		traceparent = BaseTraceparent(trace_flags = 0xff)
		self.assertEqual(traceparent.trace_flags, 0xff)

		self.assertRaises(ValueError, lambda: BaseTraceparent(trace_flags = -1))
		self.assertRaises(ValueError, lambda: BaseTraceparent(trace_flags = 0xff + 1))

	def test_from_string(self):
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('01-12345678901234567890123456789012-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('02-12345678901234567890123456789012-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('cc-12345678901234567890123456789012-1234567890123456-00')
		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('ff-12345678901234567890123456789012-1234567890123456-00'))

		traceparent = BaseTraceparent.from_string('00-00000000000000000000000000000000-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('00-ffffffffffffffffffffffffffffffff-1234567890123456-00')

		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-0000000000000000-00')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-ffffffffffffffff-00')

		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-00')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-01')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-02')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-03')
		traceparent = BaseTraceparent.from_string('00-12345678901234567890123456789012-1234567890123456-ff')

		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('0-12345678901234567890123456789012-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('000-12345678901234567890123456789012-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('00-1234567890123456789012345678901-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('00-123456789012345678901234567890123-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('00-12345678901234567890123456789012-123456789012345-00'))
		self.assertRaises(ValueError, lambda: BaseTraceparent.from_string('00-12345678901234567890123456789012-12345678901234567-00'))

	def test_repr(self):
		string = '12-12345678901234567890123456789012-1234567890123456-ff'
		traceparent = BaseTraceparent.from_string('12-12345678901234567890123456789012-1234567890123456-ff')
		self.assertEqual(repr(traceparent), 'BaseTraceparent({})'.format(repr(string)))

	def test_str(self):
		string = '12-12345678901234567890123456789012-1234567890123456-ff'
		traceparent = BaseTraceparent.from_string('12-12345678901234567890123456789012-1234567890123456-ff')
		self.assertEqual(str(traceparent), string)

	def test_set_trace_id(self):
		traceparent = BaseTraceparent()
		traceparent.set_trace_id(None)
		traceparent.set_trace_id(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
		self.assertRaises(ValueError, lambda: traceparent.set_trace_id('fffffffffffffffffffffffffffffff'))
		traceparent.set_trace_id('ffffffffffffffffffffffffffffffff')
		self.assertRaises(ValueError, lambda: traceparent.set_trace_id('fffffffffffffffffffffffffffffffff'))

	def test_set_parent_id(self):
		traceparent = BaseTraceparent()
		traceparent.set_parent_id(None)
		traceparent.set_parent_id(b'\xff\xff\xff\xff\xff\xff\xff\xff')
		self.assertRaises(ValueError, lambda: traceparent.set_parent_id('fffffffffffffff'))
		traceparent.set_parent_id('ffffffffffffffff')
		self.assertRaises(ValueError, lambda: traceparent.set_parent_id('fffffffffffffffff'))

class TraceparentTest(unittest.TestCase):
	def test_ctor_default(self):
		traceparent = Traceparent()
		self.assertEqual(traceparent.version, 0)
		self.assertNotEqual(traceparent.trace_id, b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
		self.assertNotEqual(traceparent.parent_id, b'\0\0\0\0\0\0\0\0')
		self.assertEqual(traceparent.trace_flags, 0)

	def test_ctor(self):
		self.assertRaises(ValueError, lambda: Traceparent(version = 1))
		self.assertRaises(ValueError, lambda: Traceparent(version = 0xff))
		self.assertRaises(ValueError, lambda: Traceparent(trace_id = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'))
		self.assertRaises(ValueError, lambda: Traceparent(parent_id = b'\0\0\0\0\0\0\0\0'))

	def test_from_string(self):
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-00')
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-01')
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-02')
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-03')
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-ff')
		self.assertRaises(ValueError, lambda: Traceparent.from_string('01-12345678901234567890123456789012-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: Traceparent.from_string('02-12345678901234567890123456789012-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: Traceparent.from_string('cc-12345678901234567890123456789012-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: Traceparent.from_string('ff-12345678901234567890123456789012-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: Traceparent.from_string('00-00000000000000000000000000000000-1234567890123456-00'))
		self.assertRaises(ValueError, lambda: Traceparent.from_string('00-12345678901234567890123456789012-0000000000000000-00'))

	def test_repr(self):
		string = '00-12345678901234567890123456789012-1234567890123456-ff'
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-ff')
		self.assertEqual(repr(traceparent), 'Traceparent({})'.format(repr(string)))

	def test_str(self):
		string = '00-12345678901234567890123456789012-1234567890123456-ff'
		traceparent = Traceparent.from_string('00-12345678901234567890123456789012-1234567890123456-ff')
		self.assertEqual(str(traceparent), string)

	def test_set_version(self):
		traceparent = Traceparent()
		traceparent.set_version(0)
		self.assertRaises(ValueError, lambda: traceparent.set_version(1))

	def test_set_trace_id(self):
		traceparent = Traceparent()
		self.assertRaises(ValueError, lambda: traceparent.set_trace_id(None))

	def test_set_parent_id(self):
		traceparent = Traceparent()
		self.assertRaises(ValueError, lambda: traceparent.set_parent_id(None))

if __name__ == '__main__':
	unittest.main()
