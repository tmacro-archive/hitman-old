from hitman.util.pubsub import Subscriber


def test_handler(event):
	print(event)


s = Subscriber('ipc://.hitman_events.sock')
s.open()
s.addHandler('firehose', test_handler, strict = False)
s.addHandler('msg', test_handler, strict = False)
s.addHandler('cmd', test_handler, strict = False)
input()
