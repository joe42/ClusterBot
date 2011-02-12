from xml.sax import make_parser
from xml.sax.handler import ContentHandler
"""For simple access to XML tag's attributes."""
class MyXMLReader(ContentHandler):
    def __init__(self, xmlfile):
        """Reads an XML file and stores all tags assigning all its attributes to it."""
        self.xmlfile = xmlfile;
        self.tags = {};
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(open(xmlfile))
        

    def startElement(self, tagname, attrs):
        """Called for every tag in the xml file
        Creates the dictionary self.tags which might have a dictionary of attribute-value-pairs or a list thereof.
        """
        if tagname in self.tags:
            if not isinstance(self.tags[tagname],list):
                self.tags[tagname] = [self.tags[tagname]]
                assert(self.tags[tagname] != None)
            self.tags[tagname].append(attrs);
        else:
            self.tags[tagname] = attrs;
    
    def hasAttribute(self,tagname,attributeName):
        """:returns: True iff if the tagname, attributeName combination was not found"""
        if not tagname in self.tags:
            return False;
        if isinstance(self.tags[tagname],list):
            for attributes in self.tags[tagname]:
                if attributeName in attributes:
                    return True;
        elif attributeName in self.tags[tagname]:
            return True;
        return False;
    
    def getAttribute(self,tagname,attributeName):
        """:returns: the value of the attribute <code>attributeName</code> in the tag <code>tagname</code> or a list of such values
        :raises: ValueError: if the tagname, attributeName combination was not found
        """
        ret = None
        if not self.hasAttribute(tagname, attributeName):
            raise ValueError, "No tag with the name "+tagname+" and corresponding attribute with the name "+attributeName+" was found.";
        
        if isinstance(self.tags[tagname],list):
            ret = []
            for attributes in self.tags[tagname]:
                if attributeName in attributes:
                    ret.append(attributes.get(attributeName));
        else: 
            ret = self.tags[tagname].get(attributeName);
        return ret;
