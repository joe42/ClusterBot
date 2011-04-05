"""A base class for building Python modules.
TODO: The attributes should be marked private by underscores and public setters should be written. 
These then need to be used in all subclasses as well. (Python refactoring is hard.)  
"""
class ClassBuilder(object):
    def __init__(self):
        self.className = None;
        self.pythonfile = None;
        self.parameters = {}
    
    def getConstructorParameters(self,startWithComma=False,withDefaultValues=False):
        """:param startWithComma: If True, start the returned string with a comma iff the returned string contains one or more parameters
        :param withDefaultValues: If True, every parameter in the returned string is substituted by paramM=defaultValueM, where defaultValueM is the corresponding value found in the dictionary :attr:`parameters` storing the parameter's names.
        :returns: A string of the form 'param1,param2...paramN', where param1 through paramN are all keys of :attr:`parameters` 
        """
        ret = self._getParametersFromDict(self.parameters, startWithComma, withDefaultValues);
        return ret; 
    
    def _getParametersFromDict(self, dict, startWithComma=False,withDefaultValues=False):
        """The internal method for constructing return values for :meth:`getConstructorParameters`. 
        Parameters and return values correspond, except the dict parameter, which explicitly specifies the parameter - default value pairs.
        """
        ret="";
        if len(dict) > 0:
            if startWithComma:
                ret+=", ";
            if withDefaultValues:
                ret += ' ,'.join(["%s=%s" % (name,name) for name in dict]);
            else:
                ret += ", ".join(dict)
        return ret

    def getInstanceVariableAssignments(self):
        """:returns: A string of the form 'self.param1 = defaultValue1;\\nself.param2 = defaultValue2;\\n..self.paramN = defaultValueN;\\n', where param1 through paramN are all keys of :attr:`parameters` and defaultValue1 through defaultValueN are the corresponding values.
        """
        ret="";
        if len(self.parameters) > 0:
            ret += ''.join(["self.%s = %s;\n" % (name, name) for name in self.parameters])
        return ret

    def getConstructorParameterAssignments(self):
        """Assumes the existence of a local dictionary with the name *args*.
        :returns: A statement which takes each key in :attr:`parameters` as a local variable and assigns the corresponding value of the key with the same name found in *args*.
        If there is no key with the same name in *args*, the statement assigns to it the corresponding value of :attr:`parameters` as a default value. 
        """
        ret="";
        if len(self.parameters) > 0:
            for name, value in self.parameters.items():
                if type(value) == str:
                    ret += \
"if " + name + " in args:\n\
    " + name + " = args['" + name + "'];\n\
else:\n\
    " + name + " = '" + value + "'\n"
                else:
                    ret += \
"if '" + name + "' in args:\n\
    " + name + " = args['" + name + "'];\n\
else:\n    " + name + " = " + str(value) + "\n"
        return ret