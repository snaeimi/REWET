import wntr
import numpy as np
import logging
from wntr.utils.ordered_set import OrderedSet
from wntr.sim.network_isolation import check_for_isolated_junctions, get_long_size
from wntr.sim.core import WNTRSimulator, _get_csr_data_index
from collections import OrderedDict
import itertools
import scipy.sparse.csr


logger = logging.getLogger(__name__)

class EnhancedEPANETSimulator(WNTRSimulator):
    def __init__(self, WaterNetwork):
        super(EnhancedEPANETSimulator, self).__init__(WaterNetwork, 'Anything')
        self._wn=WaterNetwork
        self._prev_isolated_junctions = OrderedSet()
        self._prev_isolated_links = OrderedSet()
        #self._internal_graph = None
        long_size = get_long_size()
        if long_size == 4:
            self._int_dtype = np.int32
        else:
            assert long_size == 8
            self._int_dtype = np.int64
    
    def _get_isolated_junctions_and_links(self, prev_isolated_junctions, prev_isolated_links):
        self._prev_isolated_junctions=prev_isolated_junctions
        self._prev_isolated_links=prev_isolated_links
        
        self._initialize_internal_graph()
        logger_level = logger.getEffectiveLevel()

        if logger_level <= logging.DEBUG:
            logger.debug('checking for isolated junctions and links')
        for j in self._prev_isolated_junctions:
            try:
                junction = self._wn.get_node(j)
                junction._is_isolated = False
            except:
                pass
        for l in self._prev_isolated_links:
            try:
                link = self._wn.get_link(l)
                link._is_isolated = False
            except:
                pass
        node_indicator = np.ones(self._wn.num_nodes, dtype=self._int_dtype)
        check_for_isolated_junctions(self._source_ids, node_indicator, self._internal_graph.indptr,
                                     self._internal_graph.indices, self._internal_graph.data,
                                     self._number_of_connections)

        isolated_junction_ids = [i for i in range(len(node_indicator)) if node_indicator[i] == 1]
        isolated_junctions = OrderedSet()
        isolated_links = OrderedSet()
        for j_id in isolated_junction_ids:
            j = self._node_id_to_name[j_id]
            junction = self._wn.get_node(j)
            junction._is_isolated = True
            isolated_junctions.add(j)
            connected_links = self._wn.get_links_for_node(j)
            for l in connected_links:
                link = self._wn.get_link(l)
                link._is_isolated = True
                isolated_links.add(l)

        if logger_level <= logging.DEBUG:
            if len(isolated_junctions) > 0 or len(isolated_links) > 0:
                raise ValueError('isolated junctions: {0}'.format(isolated_junctions))
                logger.debug('isolated links: {0}'.format(isolated_links))

        self._prev_isolated_junctions = isolated_junctions
        self._prev_isolated_links = isolated_links
        return isolated_junctions, isolated_links
    
    def _initialize_internal_graph(self):
        n_links = OrderedDict()
        rows = []
        cols = []
        vals = []
        for link_name, link in itertools.chain(self._wn.pipes(), self._wn.pumps(), self._wn.valves()):
            from_node_name = link.start_node_name
            to_node_name = link.end_node_name
            from_node_id = self._node_name_to_id[from_node_name]
            to_node_id = self._node_name_to_id[to_node_name]
            if (from_node_id, to_node_id) not in n_links:
                n_links[(from_node_id, to_node_id)] = 0
                n_links[(to_node_id, from_node_id)] = 0
            n_links[(from_node_id, to_node_id)] += 1
            n_links[(to_node_id, from_node_id)] += 1
            rows.append(from_node_id)
            cols.append(to_node_id)
            rows.append(to_node_id)
            cols.append(from_node_id)
            if link.initial_status == wntr.network.LinkStatus.closed:
                vals.append(0)
                vals.append(0)
            else:
                vals.append(1)
                vals.append(1)

        rows = np.array(rows, dtype=self._int_dtype)
        cols = np.array(cols, dtype=self._int_dtype)
        vals = np.array(vals, dtype=self._int_dtype)
        self._internal_graph = scipy.sparse.csr_matrix((vals, (rows, cols)))

        ndx_map = OrderedDict()
        for link_name, link in self._wn.links():
            from_node_name = link.start_node_name
            to_node_name = link.end_node_name
            from_node_id = self._node_name_to_id[from_node_name]
            to_node_id = self._node_name_to_id[to_node_name]
            ndx1 = _get_csr_data_index(self._internal_graph, from_node_id, to_node_id)
            ndx2 = _get_csr_data_index(self._internal_graph, to_node_id, from_node_id)
            ndx_map[link] = (ndx1, ndx2)
        self._map_link_to_internal_graph_data_ndx = ndx_map

        self._number_of_connections = [0 for i in range(self._wn.num_nodes)]
        for node_id in self._node_id_to_name.keys():
            self._number_of_connections[node_id] = self._internal_graph.indptr[node_id+1] - self._internal_graph.indptr[node_id]
        self._number_of_connections = np.array(self._number_of_connections, dtype=self._int_dtype)

        self._node_pairs_with_multiple_links = OrderedDict()
        for from_node_id, to_node_id in n_links.keys():
            if n_links[(from_node_id, to_node_id)] > 1:
                if (to_node_id, from_node_id) in self._node_pairs_with_multiple_links:
                    continue
                self._internal_graph[from_node_id, to_node_id] = 0
                self._internal_graph[to_node_id, from_node_id] = 0
                from_node_name = self._node_id_to_name[from_node_id]
                to_node_name = self._node_id_to_name[to_node_id]
                tmp_list = self._node_pairs_with_multiple_links[(from_node_id, to_node_id)] = []
                for link_name in self._wn.get_links_for_node(from_node_name):
                    link = self._wn.get_link(link_name)
                    if link.start_node_name == to_node_name or link.end_node_name == to_node_name:
                        tmp_list.append(link)
                        if link.initial_status != wntr.network.LinkStatus.closed:
                            ndx1, ndx2 = ndx_map[link]
                            self._internal_graph.data[ndx1] = 1
                            self._internal_graph.data[ndx2] = 1

        self._source_ids = []
        for node_name, node in self._wn.tanks():
            node_id = self._node_name_to_id[node_name]
            self._source_ids.append(node_id)
        for node_name, node in self._wn.reservoirs():
            node_id = self._node_name_to_id[node_name]
            self._source_ids.append(node_id)
        self._source_ids = np.array(self._source_ids, dtype=self._int_dtype)

    def _update_internal_graph(self):
        data = self._internal_graph.data
        ndx_map = self._map_link_to_internal_graph_data_ndx
        for mgr in [self._presolve_controls, self._rules, self._postsolve_controls]:
            for obj, attr in mgr.get_changes():
                if 'status' == attr:
                    if obj.status == wntr.network.LinkStatus.closed:
                        ndx1, ndx2 = ndx_map[obj]
                        data[ndx1] = 0
                        data[ndx2] = 0
                    else:
                        ndx1, ndx2 = ndx_map[obj]
                        data[ndx1] = 1
                        data[ndx2] = 1

        for key, link_list in self._node_pairs_with_multiple_links.items():
            first_link = link_list[0]
            ndx1, ndx2 = ndx_map[first_link]
            data[ndx1] = 0
            data[ndx2] = 0
            for link in link_list:
                if link.status != wntr.network.LinkStatus.closed:
                    ndx1, ndx2 = ndx_map[link]
                    data[ndx1] = 1
                    data[ndx2] = 1

    
    