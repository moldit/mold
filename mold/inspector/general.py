from twisted.internet import defer
from zope.interface import implements

from mold.interface import IInspector
from mold.error import Error


class UnknownResource(Error): pass



class DictInspector:
    """
    I pass off inspections to other inspectors based on the ``kind`` attribute
    in the inspection document.
    
    @ivar mapping: Dictionary mapping resource kinds to L{IInspector}s.
    """
    
    implements(IInspector)
    
    
    def __init__(self, mapping):
        self.mapping = mapping


    def inspect(self, params):
        """
        Inspect the resource described by C{params}.
        
        @param params: A dictionary with at least a C{kind} attribute.
        
        @rtype: Deferred
        @return: The value of the inspection or an error if there is one.
        """
        try:
            inspector = self.mapping[params['kind']]
        except KeyError as e:
            return defer.fail(UnknownResource(params.get('kind', None)))
        return defer.maybeDeferred(inspector.inspect, params)



from mold.inspector import files
inspector = DictInspector({
    'file': files.Inspector(),
})