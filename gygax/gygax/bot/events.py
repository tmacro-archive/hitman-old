from .dispatch import Event
from .const import EVENT_TYPES as ETYPES

class MessageEvent(Event):
	type  = ETYPES.MSG
	@property
	def text(self):
		return self._get('text')

	@property
	def from(self):
		return self._get('from')

