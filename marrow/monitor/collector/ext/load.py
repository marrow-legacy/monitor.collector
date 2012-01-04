# encoding: utf-8

import os
import subprocess

import mongoengine as db



def generic_backend():
    """Allow Python to handle the details of load average discovery.
    
    This is the fastest method, but may not be portable everywhere.
    
    Testing on a Linux 2.6.35 Rackspace Cloud server: 17µsec.
    """
    
    yield os.getloadavg()


def linux_backend():
    """Process the contents of /proc/loadavg.
    
    This is the second-slowest method and is only viable on Linux hosts.
    
    Testing on a Linux 2.6.35 Rackspace Cloud server: 40µsec.
    """
    
    with open('/proc/loadavg', 'r') as fh:
        yield [float(i) for i in fh.read().split(' ', 3)[:3]]


def posix_backend():
    """Process the output of the uptime command.
    
    This is by far the slowest method, only to be used under dire circumstances.
    
    Testing on a Linux 2.6.35 Rackspace Cloud server: 6.9msec.
    
    TODO: Pass the subprocess call back up to the reactor to wait for data.
    """
    
    yield [float(i) for i in subprocess.check_output(['uptime']).rpartition(': ')[2].strip().split(' ', 3)[:3]]


_map = {'generic': generic_backend, 'linux': linux_backend, 'posix': posix_backend, None: generic_backend}


class LoadMixIn(object):
    load = db.ListField(db.FloatField, verbose_name="Load Average", default=list)


class LoadExtension(object):
    def __init__(self, config):
        super(LoadExtension, self).__init__()
        
        # TODO: Standard trifecta.
        self.backend = _map[config.get('backend')]
    
    @property
    def mixin(self):
        return LoadMixIn
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def __call__(self, rec):
        for chunk in self.backend():
            if type(chunk) != list:
                yield chunk
            
            rec.load = chunk
 