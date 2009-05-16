#
#
#


from lxml import objectify

def dictify(el):
	d = {};
	d.update(el.attrib)
	for k, l in el.__dict__.iteritems():
		d[k] = [dictify(e) for e in l]
	return d
