from zope.interface import Interface, Attribute



class IConformer(Interface):
    """
    I cause machines to conform to an expected state.
    """
    
    
    def conform(params):
        """
        Cause a machine to conform to a given state prescription.
        
        @param params: A dictionary conforming to a prescription schema.
        """



class IInspector(Interface):
    """
    I inspect the current state of machines
    """
    
    
    def inspect(params, log=None):
        """
        Inspect the current state of a machine.
        
        @param params: A dictionary conforming to an inspection schema
        
        @param log: A callable that will log json-able things
        """



class ILogger(Interface):
    """
    I log execution paths from beginning to end.
    """
    
    
    def msg(message, channel=None):
        """
        Log a string message to a particular channel.
        
        @param message: A string message
        @param channel: A string name identifying a channel
        """


    def json(data, channel=None):
        """
        Log some data as json to a particular channel
        
        @param data: A json-able message
        @param channel: A string name identifying a channel
        """


    def startStep(title, data=None):
        """
        Indicate that a step was begun.
        
        @param title: title of the step just begun
        @param data: Optional json-able data indicating run-time parameters
        """


    def addFile(name, fh):
        """
        Attach a file to this log
        
        @param name: Name of the file as it should be reported
        @param fh: A file-like object that will be read for the file data.
        """


    def addLink(name, href):
        """
        Add a link to this log
        
        @param name: Name of the link
        @param href: href of the link
        """


