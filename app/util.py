import time


class Timer:
	def __enter__(self):
		self.start = time.clock()
		return self

	def __exit__(self, *args):
		self.end = time.clock()
		self.interval = self.end - self.start


class TimerPrint(Timer):
	def __init__(self, msg="Timer"):
		self.msg = msg

	def __exit__(self, *args):
		Timer.__exit__(self)
		print self.msg + ":", str(round(self.interval * 1000, 3)) + "ms"


def is_valid_move(possible_move, data):

	# at round 1, our head == our tail, so run this check before the next one
	if possible_move == data['oursnake']['coords'][0]:
		return False

	if possible_move == data['oursnake']['coords'][-1]:
		#it's fine to chase our tail
		return True

	if possible_move in data['oursnake']['coords']:
		return False

	if possible_move[0] < 0 or possible_move[0] >= data['width'] or possible_move[1] < 0 or possible_move[1] >= data['height']:
		return False
	return True

def dist(a, b):
	return abs(b[0] - a[0]) + abs(b[1] - a[1])


def bad_move():
	return False, 9995
