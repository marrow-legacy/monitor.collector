# encoding: utf-8

import os
import subprocess

import mongoengine as db

try:
    from itertools import izip as zip
except ImportError: # pragma: no cover
    pass



class CPUDetail(db.EmbeddedDocument):
    user = db.FloatField(db_field='u', verbose_name="Userspace Percentage")
    nice = db.FloatField(db_field='n', verbose_name="Low-Priority Percentage")
    system = db.FloatField(db_field='s', verbose_name="System Percentage")
    iowait = db.FloatField(db_field='io', verbose_name="IO-Blocked Percentage")
    irq = db.FloatField(db_field='hi', verbose_name="IRQ Percentage")
    soft = db.FloatField(db_field='si', verbose_name="Soft IRQ Percentage")
    steal = db.FloatField(db_field='vs', verbose_name="Sibling VM Percentage")
    guest = db.FloatField(db_field='vg', verbose_name="Child VM Percentage")
    idle = db.FloatField(db_field='i', verbose_name="Idle Percentage")
    
    _fmap = dict(user='%usr', nice='%nice', system='%sys',
            iowait='%iowait', irq='%irq', soft='%soft',
            steal='%steal', guest='%guest', idle='%idle')
    _ifmap = dict(zip(_fmap.values(), _fmap))
    
    def __repr__(self):
        fmap = self._fmap
        parts = []
        
        for attr in fmap:
            value = getattr(self, attr, None)
            if value is None: continue
            parts.append("%1.2f %s" % (value, fmap[attr]))

        return "<CPUDetail %s>" % ', '.join(parts)


class CPUMixIn(object):
    # This list will be len(n+1) where n is the number of cores.
    # The first value represents the aggregate across all cores.
    cpu = db.ListField(db.EmbeddedDocumentField(db.EmbeddedDocument), verbose_name="Processor Information", default=list)


def mpstat_backend():
    """Parse the output of the mpstat program.
    
    Testing on a Linux 2.6.35 Rackspace Cloud server: 1s
    """
    
    # Linux 2.6.35.4-rscloud (tabris.lesite.ca) 	01/03/2012 	_x86_64_	(4 CPU)
    # 
    # 09:19:08 PM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest   %idle
    # 09:19:09 PM  all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # 09:19:09 PM    0    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # 09:19:09 PM    1    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # 09:19:09 PM    2    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # 09:19:09 PM    3    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # 
    # Average:     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest   %idle
    # Average:     all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # Average:       0    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # Average:       1    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # Average:       2    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    # Average:       3    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
    
    # TODO: Offload IO to the coroutine reactor.
    
    _ifmap = CPUDetail._ifmap
    mappings = []
    result = subprocess.check_output(['mpstat', '-P', 'ALL', '1', '1'])
    
    for line in result.split('\n'):
        if not line.startswith('Average:'):
            continue
        
        parts = line.replace('  ', ' ').replace('  ', ' ').split()[2:]
        
        if not mappings:
            mappings = [_ifmap.get(i) for i in parts]
            continue
        
        detail = dict()
        
        for attr, part in zip(mappings, parts):
            if not attr: continue
            detail[attr] = float(part) / 100.0
        
        yield CPUDetail(**detail)


_map = {'mpstat': mpstat_backend, None: mpstat_backend}


class CPUExtension(object):
    def __init__(self, config):
        super(CPUExtension, self).__init__()
        
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
        rec.cpu = list()
        
        for chunk in self.backend():
            if not isinstance(chunk, db.EmbeddedDocument):
                yield chunk
            
            rec.cpu.append(chunk)
