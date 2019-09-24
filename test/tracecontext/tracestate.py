from collections import OrderedDict
import re

class Tracestate(object):
	_KEY_WITHOUT_VENDOR_FORMAT = r'[a-z][_0-9a-z\-\*\/]{0,255}'
	_KEY_WITH_VENDOR_FORMAT = r'[0-9a-z][_0-9a-z\-\*\/]{0,240}@[a-z][_0-9a-z\-\*\/]{0,13}'
	_KEY_FORMAT = _KEY_WITHOUT_VENDOR_FORMAT + '|' + _KEY_WITH_VENDOR_FORMAT
	_VALUE_FORMAT = r'[\x20-\x2b\x2d-\x3c\x3e-\x7e]{0,255}[\x21-\x2b\x2d-\x3c\x3e-\x7e]'
	_DELIMITER_FORMAT_RE = re.compile('[ \t]*,[ \t]*')
	_KEY_VALIDATION_RE = re.compile('^(' + _KEY_FORMAT + ')$')
	_VALUE_VALIDATION_RE = re.compile('^(' + _VALUE_FORMAT + ')$')
	_MEMBER_FORMAT_RE = re.compile('^(%s)(=)(%s)$'%(_KEY_FORMAT, _VALUE_FORMAT))

	def __init__(self, *args, **kwds):
		if len(args) == 1 and not kwds:
			if isinstance(args[0], str):
				self._traits = OrderedDict()
				self.from_string(args[0])
				return
			if isinstance(args[0], Tracestate):
				self._traits = OrderedDict(args[0]._traits)
				return
		self._traits = OrderedDict(*args, **kwds)

	def __len__(self):
		return len(self._traits)

	def __repr__(self):
		return '{}({!r})'.format(type(self).__name__, str(self))

	def __getitem__(self, key):
		return self._traits[key]

	def __setitem__(self, key, value):
		if not isinstance(key, str):
			raise ValueError('key must be an instance of str')
		if not re.match(self._KEY_VALIDATION_RE, key):
			raise ValueError('illegal key provided')
		if not isinstance(value, str):
			raise ValueError('value must be an instance of str')
		if not re.match(self._VALUE_VALIDATION_RE, value):
			raise ValueError('illegal value provided')
		self._traits[key] = value
		self._traits.move_to_end(key, last = False)

	def __str__(self):
		return self.to_string()

	def from_string(self, string):
		for member in re.split(self._DELIMITER_FORMAT_RE, string):
			if member:
				match = self._MEMBER_FORMAT_RE.match(member)
				if not match:
					raise ValueError('illegal key-value format {!r}'.format(member))
				key, eq, value = match.groups()
				if key in self._traits:
					raise ValueError('conflict key {!r}'.format(key))
				self._traits[key] = value
		return self

	def to_string(self):
		return ','.join(map(lambda key: key + '=' + self[key], self._traits))

	# make this an optional choice instead of enforcement during put/update
	# if the tracestate value size is bigger than 512 characters, the tracer
	# CAN decide to forward the tracestate
	def is_valid(self):
		if len(self) is 0:
			return False
		# combined header length MUST be less than or equal to 512 bytes
		if len(self.to_string()) > 512:
			return False
		# there can be a maximum of 32 list-members in a list
		if len(self) > 32:
			return False
		return True

	def pop(self):
		return self._traits.popitem()
