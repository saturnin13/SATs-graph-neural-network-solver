import random

from C_GNNs.gnns.repeating_nnconv_gnn import RepeatingNNConvGNN
import torch.nn.functional as F


class VariableRepeatingNNConvGNN(RepeatingNNConvGNN):

    def __init__(self, sigmoid_output=True, dropout_prob=0.5, deep_nn=False, num_hidden_neurons=8,
                 conv_min_max_rep=(10, 20), ratio_test_train_rep=4):
        super().__init__(sigmoid_output, dropout_prob, deep_nn, num_hidden_neurons, conv_min_max_rep[1],
                         ratio_test_train_rep)
        self._conv_min_max_rep = conv_min_max_rep

    def _iterate_nnconv(self, x, edge_index, edge_attr):
        if self.training:
            iteration_number = random.randint(self._conv_min_max_rep[0], self._conv_min_max_rep[1])
        else:
            iteration_number = self._conv_repetition * self._ratio_test_train_rep

        for i in range(iteration_number):
            x = F.dropout(x, p=self._dropout_prob, training=self.training)
            x = F.leaky_relu(self._conv2(x, edge_index, edge_attr))
