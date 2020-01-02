from abc import ABC, abstractmethod

import torch
from torch_geometric.nn import global_add_pool, global_mean_pool, global_max_pool

from C_GNN.gnn_enums.pooling import Pooling
from utils.abstract_repr import AbstractRepr

# TODO: add options for the pooling
class AbstractGNN(torch.nn.Module, ABC, AbstractRepr):

    def __init__(self, sigmoid_output=True, dropout_prob=0.5, pooling=Pooling.GLOBAL_ADD, num_hidden_neurons=8):
        '''
        Defines the GNN architecture.
        :param sigmoid_output: Whether to output a sigmoid.
        :param dropout_prob: The probability of dropout.
        '''
        super(AbstractGNN, self).__init__()
        self._sigmoid_output = sigmoid_output
        self._dropout_prob = dropout_prob
        self.__pooling = pooling
        self._num_hidden_neurons = num_hidden_neurons

    def _get_fields_for_repr(self):
        return {
            "sigmoid_output": self._sigmoid_output,
            "dropout_prob": self._dropout_prob,
            "pooling": self._pooling.__name__,
            "num_hidden_neurons": self._num_hidden_neurons
        }

    @property
    def _pooling(self):
        if self.__pooling == Pooling.GLOBAL_ADD:
            return global_add_pool
        elif self.__pooling == Pooling.GLOBAL_MEAN:
            return global_mean_pool
        elif self.__pooling == Pooling.GLOBAL_MAX:
            return global_max_pool

    # Initialise the dynamic part of the data later in a method so that we can build the object in the config, this
    # could be replaced by a constructor pattern
    @abstractmethod
    def initialise_channels(self, in_channels, out_channels, num_edge_features=None):
        self._in_channels = in_channels
        self._out_channels = out_channels
        self._num_edge_features = num_edge_features

    def forward(self, data):
        x, edge_index, edge_attr, batch = data.x, data.edge_index, data.edge_attr, data.batch

        x = self._perform_pre_pooling(x, edge_index, edge_attr)
        x = self.__perform_pooling(x, batch)
        x = self._perform_post_pooling(x, edge_index, edge_attr)

        return torch.sigmoid(x) if self._sigmoid_output else x

    @abstractmethod
    def _perform_pre_pooling(self, x, edge_index, edge_attr):
        pass

    def __perform_pooling(self, x, batch):
        return self._pooling(x, batch)

    @abstractmethod
    def _perform_post_pooling(self, x, edge_index, edge_attr):
        pass