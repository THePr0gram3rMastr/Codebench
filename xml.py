#
#
#
import logging

from lxml import etree
from lxml import objectify

logger = logging.getLogger(__name__)

def dictify(el):
	d = {};
	d.update(el.attrib)
	for k, l in el.__dict__.iteritems():
		d[k] = [dictify(e) for e in l]
	return d

def build_element(root, cval):
    """
    This method build the element depending on the type of the value
    """
    if isinstance(cval, XMLify):
            root.append(cval.XMLDescription())
    elif hasattr(cval, '__iter__'):
        for sval in cval:
            c = etree.Element(root.tag[:-1])
            c.text = sval
            root.append(c)
    else:
        root.text = None if cval is None else str(cval)

class XMLify(object):
    """
    This class provide 2 method for updating and describing a python object as a
    leaf Element. 
    """
    xml_attributes = []
    xml_childs = []
    xml_tag = "undefined"

    xml_updatable = []

    repr_attrs = []

    def __repr__(self):
        res =  object.__repr__(self) + ' { '
        for attr in self.repr_attrs:
            res += " %s : %s," % (attr, getattr(self, attr))
        return res[:-1] + ' }'


    def XMLDescription(self):
        """
        This method return the Element describing the leaf object based on
        attributes defined in xml_attributes and xml_childs.
        """
        element = etree.Element(self.xml_tag)
        for a in self.xml_attributes:
            element.attrib[a] = str(getattr(self, a))
        for ctag in self.xml_childs:
            ce = etree.Element(ctag)
            cval = getattr(self, ctag)
            build_element(ce, str(cval))
            element.append(ce)
        return element


    def updateFromXML(self, xmlobj):
        """
        This method update values based on the xmlobj passed as an argument.
        Only update the valus of updatable variables.
        """
        for obj in xmlobj:
            if obj.tag in self.xml_updatable:
                val = '' if obj.text is None else obj.text
                setattr(self, obj.tag, val)
            else:
                if logger.isEnabledFor(logging.WARNING): 
                    logger.warning("Trying to update an unupdatable attribute -- %s -- " % obj.tag)



