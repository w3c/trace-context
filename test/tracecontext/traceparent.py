import re
import uuid

class BaseTraceparent(object):
	_VERSION_FORMAT_RE = re.compile('^[0-9a-f]{2}$')
	_TRACE_ID_FORMAT_RE = re.compile('^[0-9a-f]{32}$')
	_PARENT_ID_FORMAT_RE = re.compile('^[0-9a-f]{16}$')
	_TRACE_FLAGS_FORMAT_RE = re.compile('^[0-9a-f]{2}$')
	_ZERO_TRACE_ID = b'\0' * 16
	_ZERO_PARENT_ID = b'\0' * 8

	def __init__(self, version = 0, trace_id = None, parent_id = None, trace_flags = 0, *_residue):
		self.version = version
		self.trace_id = trace_id
		self.parent_id = parent_id
		self.trace_flags = trace_flags
		self._residue = _residue

	def __repr__(self):
		return '{}({!r})'.format(type(self).__name__, str(self))

	def __str__(self):
		return self.to_string()

	@classmethod
	def from_string(cls, value):
		if not isinstance(value, str):
			raise ValueError('value must be a string')
		value = value.split('-')
		return cls(*value)

	def to_string(self):
		retval = '{}-{}-{}-{}'.format(self._version.hex(), self._trace_id.hex(), self._parent_id.hex(), self._trace_flags.hex())
		if self._residue:
			retval += '-' + '-'.join(self._residue)
		return retval

	def get_version(self):
		return ord(self._version)

	def set_version(self, version):
		if isinstance(version, bytes):
			if len(version) != 1:
				raise ValueError('version must be a single byte')
			if version == b'\xff':
				raise ValueError('version 255 is now allowed')
			self._version = version
		elif isinstance(version, int):
			if version < 0 or version > 254:
				raise ValueError('version must be within range [0, 255)')
			self.set_version(bytes([version]))
		elif isinstance(version, str):
			if not self._VERSION_FORMAT_RE.match(version):
				raise ValueError('version {!r} does not match {}'.format(version, self._VERSION_FORMAT_RE))
			self.set_version(bytes.fromhex(version))
		else:
			raise ValueError('unsupported version type')

	def get_trace_id(self):
		return self._trace_id

	def set_trace_id(self, trace_id):
		if trace_id is None:
			self.set_trace_id(self._ZERO_TRACE_ID)
		elif isinstance(trace_id, bytes):
			if len(trace_id) != 16:
				raise ValueError('trace_id must contain 16 bytes')
			self._trace_id = trace_id
		elif isinstance(trace_id, str):
			if not self._TRACE_ID_FORMAT_RE.match(trace_id):
				raise ValueError('trace_id does not match {}'.format(self._TRACE_ID_FORMAT_RE))
			self.set_trace_id(bytes.fromhex(trace_id))
		else:
			raise ValueError('unsupported trace_id type')

	def get_parent_id(self):
		return self._parent_id

	def set_parent_id(self, parent_id):
		if parent_id is None:
			self.set_parent_id(self._ZERO_PARENT_ID)
		elif isinstance(parent_id, bytes):
			if len(parent_id) != 8:
				raise ValueError('parent_id must contain 8 bytes')
			self._parent_id = parent_id
		elif isinstance(parent_id, str):
			if not self._PARENT_ID_FORMAT_RE.match(parent_id):
				raise ValueError('parent_id does not match {}'.format(self._PARENT_ID_FORMAT_RE))
			self.set_parent_id(bytes.fromhex(parent_id))
		else:
			raise ValueError('unsupported parent_id type')

	def get_trace_flags(self):
		return ord(self._trace_flags)

	def set_trace_flags(self, trace_flags):
		if isinstance(trace_flags, bytes):
			if len(trace_flags) != 1:
				raise ValueError('trace_flags must be a single byte')
			self._trace_flags = trace_flags
		elif isinstance(trace_flags, int):
			if trace_flags < 0 or trace_flags > 255:
				raise ValueError('trace_flags must be within range [0, 255]')
			self.set_trace_flags(bytes([trace_flags]))
		elif isinstance(trace_flags, str):
			if not self._TRACE_FLAGS_FORMAT_RE.match(trace_flags):
				raise ValueError('trace_flags {!r} does not match {}'.format(trace_flags, self._TRACE_FLAGS_FORMAT_RE))
			self.set_trace_flags(bytes.fromhex(trace_flags))
		else:
			raise ValueError('unsupported trace_flags type')

	version = property(get_version, set_version)
	trace_id = property(get_trace_id, set_trace_id)
	parent_id = property(get_parent_id, set_parent_id)
	trace_flags = property(get_trace_flags, set_trace_flags)

class Traceparent(BaseTraceparent):
	def __init__(self, version = 0, trace_id = None, parent_id = None, trace_flags = 0):
		if trace_id is None:
			trace_id = uuid.uuid1().hex
		if parent_id is None:
			parent_id = uuid.uuid4().hex[:16]
		super().__init__(version, trace_id, parent_id, trace_flags)

	def set_version(self, version):
		if version != 0 and version != b'\0' and version != '00':
			raise ValueError('unsupported version')
		super().set_version(version)

	def set_trace_id(self, trace_id):
		if trace_id == self._ZERO_TRACE_ID:
			raise ValueError('all zero trace_id is not allowed')
		super().set_trace_id(trace_id)

	def set_parent_id(self, parent_id):
		if parent_id == self._ZERO_PARENT_ID:
			raise ValueError('all zero parent_id is not allowed')
		super().set_parent_id(parent_id)

	def set_trace_flags(self, trace_flags):
		super().set_trace_flags(trace_flags)

	version = property(BaseTraceparent.get_version, set_version)
	trace_id = property(BaseTraceparent.get_trace_id, set_trace_id)
	parent_id = property(BaseTraceparent.get_parent_id, set_parent_id)
	trace_flags = property(BaseTraceparent.get_trace_flags, set_trace_flags)
