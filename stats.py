class IncrementalStatistic(object):
	__n__ = 0
	__mean__ = 0
	__sumsq__ = 0
	def __call__(self, x):
		self.__n__, self.__mean__, self.__sumsq__ = incremental(self.__n__, self.__mean__, self.__sumsq__, x)

	def __get_variance__(self):
		return self.__sumsq__ / float(self.__n__)
	var = property(__get_variance__)

	def __get_mean__(self):
		return self.__mean__
	mean = property(__get_mean__)


def incremental(n, mean, sumsq, x):
	n += 1
	dev = x - mean
	mean += dev / n
	sumsq += dev * (x - mean)
	return n, mean , sumsq

