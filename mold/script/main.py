from twisted.python import usage


from mold.script import run


class Options(usage.Options):


    optParameters = [
        ('target', 't', None,
            "Target this machine.  May be specified multiple times."),
        ('inventory-file', 'i', '/etc/mold/inventory',
            "Inventory file"),
    ]


    subCommands = [
        ('run', None, run.Options, "Run a single remote command."),
        
        ('begin', None, None, "Begin a run."),
        ('end', None, None, "End a run (previously begun with begin)."),
    ]


def main():
    options = Options()
    options.parseOptions()
    if options.subCommand == 'run':
        run.main(options.subOptions, options)