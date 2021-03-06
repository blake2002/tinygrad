#!/usr/bin/env python
# see https://github.com/Matuzas77/MNIST-0.17/blob/master/MNIST_final_solution.ipynb
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'test'))

from tinygrad.tensor import Tensor
from tinygrad.nn import BatchNorm2D
from tinygrad.utils import get_parameters
import tinygrad.optim as optim

# TODO: abstract this generic trainer out of the test
from test_mnist import train as train_on_mnist

GPU = os.getenv("GPU") is not None

class SeriousModel:
  def __init__(self):
    self.blocks = 3
    self.block_convs = 3
    self.chans = 128

    self.convs = [Tensor.uniform(self.chans, self.chans if i > 0 else 1, 3, 3) for i in range(self.blocks * self.block_convs)]
    # TODO: Make batchnorm work at train time
    #self.bn = [BatchNorm2D(self.chans) for i in range(3)]
    self.fc = Tensor.uniform(self.chans, 10)

  def forward(self, x):
    x = x.reshape(shape=(-1, 1, 28, 28)) # hacks
    for i in range(self.blocks):
      for j in range(self.block_convs):
        # TODO: should padding be used?
        x = x.conv2d(self.convs[i*3+j]).relu()
      #x = self.bn[i](x)
      if i > 0:
        x = x.avg_pool2d(kernel_size=(2,2))
    # TODO: Add concat support to concat with max_pool2d
    x = x.avg_pool2d(kernel_size=x.shape[2:4])
    x = x.reshape(shape=(-1, x.shape[1]))
    x = x.dot(self.fc).logsoftmax()
    return x

if __name__ == "__main__":
  model = SeriousModel()
  params = get_parameters(model)
  print(len(params))
  if GPU:
    [x.cuda_() for x in params]
  optimizer = optim.Adam(params, lr=0.001)
  train_on_mnist(model, optimizer, steps=1875, BS=32, gpu=GPU)

