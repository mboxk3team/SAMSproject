# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Alexey Karyabkin.
# This file is part of System Analysis of eMail messageS (SAMS)
# See the file 'docs/LICENSE' for copying permission.

import hashlib
import os
import logging
#from futils import File
#from lib.profilemalware import ProfileMalware
#from lib.sandbox import SandBox
#from parseexres import ParseTE
#from parseexres import ParseTH
from lib.extsrc import VirusTotal
#from postmailer import PostMailer
#from iocmanager import IocManager
#from analysisdata import AnalysisDataMgr
from lib.core.sandbox import SandBox
from lib.categoryfilters import ExtExecFilters
from lib.common.constants import _ROOT
from lib.common.constants import WHITE_LIST_FLAG, INCIDENT_TRUE_FLAG, AGRINFO_POSITIVE_FLAG, YARA_DETECT_FLAG, SUSPECT_FTYPE_FLAG, NET_ACTIVITY_FLAG, AMOUNT_ITEMS_FLAG 


log = logging.getLogger(__name__)

try:
    import yara
    YARA_INIT = True
except ImportError:
    YARA_INIT = False

try:
    import pyclamd
    AV_INIT = True
except ImportError:
    AV_INIT = False
    


class AVScanner(object):
    """
        AntiVirus Scanner
    """
    def __init__(self):
        log.setLevel(logging.INFO)
        log.info('Initialize module AntiVirus Scanner')
        self.avs = None
        if AV_INIT:
            if self.initialize():
                log.info(self.avs.version())
                log.info('AntiVirus Scanner done')
            else:
                log.info('AntiVirus Scanner initialize failed')
        else:
            log.info('AntiVirus Scanner initialize failed')


    def initialize(self):
        self.avs = pyclamd.ClamdUnixSocket()
        if self.avs.ping():
            return True
        else:
            return False

    def scan_file(self, filename):
        if AV_INIT:
            return self.avs.scan_file(filename)
        else:
            log.info('AntiVirus Scanner initialize failed')
        
    def scan_dir(self, dirname):
        if AV_INIT:
            return self.avs.contscan_file(dirname)
        else:
            log.info('AntiVirus Scanner initialize failed')
            return None
        
    def update_avdb(self):
        self.avs.reload()
        self.avs.version()
        return True

class YARAScanner(object):
    """
        AntiVirus Scanner
    """
    def __init__(self):
        log.setLevel(logging.INFO)
        log.info('Initialize module YARA Scanner')
        self.rules = {}
        if YARA_INIT:
            if self.initialize():
                log.info('YARA Scanner done')
            else:
                log.info('YARA Scanner initialize failed')
        else:
            log.info('YARA Scanner initialize failed')


    def initialize(self):
        rulepath = os.path.join(_ROOT, 'data','yara','rules')
        ruleindex = os.path.join(_ROOT, 'data','yara','indexes.yar')
        if os.path.exists(ruleindex):
            log.info('Exist compiled YARA rules')
            try:
                self.rules = yara.load(ruleindex)
                return True
            except:
                return False
        else:
            self.rules = self.build_rules(rulepath)
            log.info('YARA rules compiled')
            self.rules.save(ruleindex)
            return True
    
    def build_rules(self, rulepath):
        rules = dict()
        for item in os.listdir(rulepath):
            rules[item] = os.path.join(_ROOT, 'data','yara', 'rules', item)
        return yara.compile(filepaths=rules)
        
    def match(self, listf):
        matches = dict()
        for filename in list(listf):
            try:
                rscan = self.rules.match(filename,timeout=60)
                if len(rscan)> 0:
                    matches[filename] = rscan
                #pass
            except Exception as e:
                log.error('Processing failed: %s' % e) 
        if len(matches) > 0:
            return matches
        return None
