from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass
from zope.interface import implements


from mold.interface import IInspector
from mold.inspector.general import DictInspector, UnknownResource, inspector



class FakeInspector:

    implements(IInspector)
    
    
    def __init__(self):
        self.inspected = []
    
    
    def inspect(self, params):
        self.inspected.append(params)
        return 'foo'



class FakeInspectorTest(TestCase):


    def test_IInspector(self):
        verifyClass(IInspector, FakeInspector)



class DictInspectorTest(TestCase):


    def test_IInspector(self):
        verifyClass(IInspector, DictInspector)


    def test_basic(self):
        """
        A DictInspector should fork on the `kind` attribute to choose another
        inspector.
        """
        i = FakeInspector()
        di = DictInspector({
            'foo': i,
        })
        
        params = {'kind': 'foo', 'name': 'bar'}
        
        def check(result):
            self.assertEqual(i.inspected, [params])
            self.assertEqual(result, 'foo')
        
        return di.inspect(params).addCallback(check)


    def test_unknownresource(self):
        """
        If you try to inspect a kind of resource not registered with the
        DictInspector, it will cause an error.
        """
        di = DictInspector({})
        params = {'kind': 'foo', 'name': 'bar'}
        return self.assertFailure(di.inspect(params), UnknownResource)



class inspectorTest(TestCase):


    def test_DictInspector(self):
        self.assertTrue(isinstance(inspector, DictInspector))
