import random
import string

def random_string(size):
	return ''.join([random.choice(string.letters + string.digits) for i in range(1, size)])
