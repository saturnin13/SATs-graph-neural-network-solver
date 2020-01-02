from C_GNN.abstract_gnn import AbstractGNN
from C_GNN.gnn_enums.pooling import Pooling
from C_GNN.gnns.edge_atr_gnns_enums.aggr import Aggr


class AbstractEdgeAttrGNN(AbstractGNN):
    def __init__(self, sigmoid_output=True, dropout_prob=0.5, pooling=Pooling.GLOBAL_ADD, num_hidden_neurons=8, deep_nn=True, aggr=Aggr.ADD):
        '''
        Defines a GNN architecture which uses the node attr, the edge index and teh edge attr.
        :param sigmoid_output: Whether to output a sigmoid.
        :param dropout_prob: The probability of dropout.
        :param deep_nn: Whether to use a deep neural net of shallow one.
        :param num_hidden_neurons: The number of hidden neurons in the hidden layers.
        :param aggr: The aggregation to use for the feed forward neural network.
        '''
        super().__init__(sigmoid_output, dropout_prob, pooling, num_hidden_neurons)
        self._deep_nn = deep_nn
        self._aggr = aggr

    def _get_fields_for_repr(self):
        return {**super()._get_fields_for_repr(),
                **{
                   "deep_nn": self._deep_nn,
                    "aggr": self._aggr
                }}
