# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 19:10:35 2020

@author: snaeimi
"""

import io
import pandas as pd


class RestorationIO():
    def __init__(self, definition_file= "Config.txt"):
        """
        Needs a file that contains:

        Parameters
        ----------
        definition_file : str
            path for tegh definition file.

        Returns
        -------
        None.

        """
        
        #some of the following lines have been addopted from WNTR
        expected_sections=['FILES']
        self.config_file_comment = []
        self.edata = []       
        
        self.sections = OrderedDict()
        for sec in expected_sections:
            self.sections[sec] = []
        
        section = None
        lnum = 0
        edata = {'fname': filename}
        with io.open(filename, 'r', encoding='utf-8') as f:
            for line in f:
            lnum += 1
            edata['lnum'] = lnum
            line = line.strip()
            nwords = len(line.split())
            if len(line) == 0 or nwords == 0:
                # Blank line
                continue
            elif line.startswith('['):
                vals = line.split(None, 1)
                sec = vals[0].upper()
                edata['sec'] = sec
                if sec in expected_sections:
                    section = sec
                    continue
                elif sec == '[END]':
                    section = None
                    break
                else:
                    raise RuntimeError('%(fname)s:%(lnum)d: Invalid section "%(sec)s"' % edata)
            elif section is None and line.startswith(';'):
                self.config_file_comment.append(line[1:])
                continue
            elif section is None:
                logger.debug('Found confusing line: %s', repr(line))
                raise RuntimeError('%(fname)s:%(lnum)d: Non-comment outside of valid section!' % edata)
            # We have text, and we are in a section
            self.sections[section].append((lnum, line))

        # Parse each of the sections

        ### Config
        self._read_config()
        
    def _read_config(self):
        """
        reads config files which contains general specification of
        configurations

        Raises
        ------
        RuntimeError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        for lnum, line in self.sections['FILES']:
            edata['lnum'] = lnum
            words, comments = _split_line(line)
            if words is not None and len(words) > 0:
                if len(words) < 2:
                    edata['key'] = words[0]
                    raise RuntimeError('%(fname)s:%(lnum)-6d %(sec)13s no value provided for %(key)s' % edata)
                key = words[0].upper()
                
                if key == "DEMAND_NODES":
                    self._demand_Node_file_name = words[0]
                    _read_demand_nodes()
                    
                    
    def _read_demand_nodes(self):
        titles = []
        ntitle = 0
        with io.open(self._demand_Node_file_name, 'r', encoding='utf-8') as f:
            for line in f:
                lnum += 1
                line = line.strip()
                nwords = len(line.split())
                words = line.split()
                dtemp=[]
                if len(line) == 0 or nwords == 0:
                    # Blank line
                    continue
                elif line.upper().startswith('NODEID'):
                    title = words.copy()
                    ntitle = len(words) #we need this to confirm that every line has data for every title(column)
                    continue
                elif nwords != ntitle:
                    raise ValueError('%{fname}s:%(lnum)d: Number of data does not match number of titles')
                elif nwords == ntitle:
                    dtemp.append(nwords)
                else:
                    raise ValueError('%{fname}s:%(lnum)d:This error must nnever happen')
        
            self.demand_node = pd.DataFrame(dtemp, columns=title)