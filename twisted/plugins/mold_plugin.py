from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker('mold', 'mold.twistd', 'Moldy Daemons', 'mold')