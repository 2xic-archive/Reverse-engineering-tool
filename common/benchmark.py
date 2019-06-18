

import time

def give_time(f):
	def wrap(*args):
		time_1 = time.time()
		ret = f(*args)
		time_2 = time.time()
		print('{:s} time usage {:.3f} s, {:.3f} ms'.format(f.__name__, (time_2 - time_1), (time_2 - time_1) * 1000.0))
		return ret
	return wrap

@give_time
def test(sleep_duration=5):
	time.sleep(sleep_duration)


if __name__ == "__main__":
	test()
	
