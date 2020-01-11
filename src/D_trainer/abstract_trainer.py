import time
from abc import ABC, abstractmethod
import torch
from torch import nn
from utils import logger
from utils.abstract_repr import AbstractRepr
import torch.nn.functional as F

try:
    from apex import amp, optimizers
except ImportError:
    logger.get().error("The apex package could not be imported, the experiment cannot be run with amp activated.")


class AbstractTrainer(ABC, AbstractRepr):
    def __init__(self, learning_rate, weight_decay, device, activate_amp, bce_loss):
        '''
        Trainer for the network.
        :param learning_rate: The learning rate.
        :param weight_decay: The weight decay.
        :param device: The device used.
        '''
        self._learning_rate = learning_rate
        self._weight_decay = weight_decay
        self._device = device
        self._activate_amp = activate_amp
        self._bce_loss = bce_loss

    def _get_fields_for_repr(self):
        return {
            "learning_rate": "{:.5f}".format(self._learning_rate),
            "weight_decay": "{:.5f}".format(self._weight_decay)
        }

    @abstractmethod
    def _create_optimizer(self, parameters, learning_rate, weight_decay):
        pass

    def train(self, number_of_epochs, model, train_loader, model_evaluator):
        logger.get().info("Starting the training")

        optimizer = self._create_optimizer(model.parameters(), self._learning_rate, self._weight_decay)

        if self._activate_amp:
            model, optimizer = amp.initialize(model, optimizer, opt_level="O1")

        train_loss = []
        test_loss = []
        accuracy = []
        start_time = time.time()
        last_epoch = 0

        try:
            for epoch in range(number_of_epochs):
                model.train()

                self._set_learning_rate(epoch, self._learning_rate, optimizer)

                current_train_loss = self._training_step(model, train_loader, optimizer)

                model.eval()
                current_test_loss, current_accuracy, _ = self._testing_step(model_evaluator, current_train_loss,
                                                                         time.time() - start_time, model, epoch)

                train_loss.append(current_train_loss)
                test_loss.append(current_test_loss)
                accuracy.append(current_accuracy)
                last_epoch = epoch
        except KeyboardInterrupt:
            train_loss, test_loss, accuracy = self.__check_same_length_else_correct(train_loss, test_loss, accuracy)

        logger.get().info("Training completed")
        return train_loss, test_loss, accuracy, time.time() - start_time, last_epoch

    @abstractmethod
    def _training_step(self, model, train_loader, optimizer):
        train_error = 0

        progress = 0
        for batch in train_loader:
            print(type(batch))
            progress += 1
            logger.get().debug("Training at: {:.1f}%\r".format(progress/len(train_loader) * 100))

            #gpu_batch = batch.to(self._device)

            optimizer.zero_grad()

            out = model(batch)

            if self._bce_loss:
                loss = nn.BCELoss()(out, batch.y.view(-1, 1))
            else:
                loss = F.mse_loss(out, batch.y.view(-1, 1))  # F.nll_loss(out, batch.y)
            train_error += loss

            if self._activate_amp:
                with amp.scale_loss(loss, optimizer) as scaled_loss:
                    scaled_loss.backward()
            else:
                loss.backward()
            optimizer.step()

        return train_error / len(train_loader)

    @abstractmethod
    def _testing_step(self, model_evaluator, current_train_loss, time, model, epoch):
        with torch.no_grad():
            return model_evaluator.eval(model, current_train_loss, do_print=True, time=time, epoch=epoch)

    def __check_same_length_else_correct(self, train_loss, test_loss, accuracy):
        train_loss = train_loss[0:-1]if len(train_loss) > len(accuracy) else train_loss
        test_loss = test_loss[0:-1] if len(test_loss) > len(accuracy) else test_loss

        return train_loss, test_loss, accuracy

    @abstractmethod
    def _set_learning_rate(self, epoch, learning_rate, optimizer):
        pass

