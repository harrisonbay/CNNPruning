# -*- coding: utf-8 -*-
"""Copy of Pruning

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15airpRfUj7yiWfbteOr7S2niqaZu3ubg
"""

from google.colab import drive
drive.mount('/gdrive/', force_remount=True)
!ls /gdrive/

import os

# BASE_PATH = '/gdrive/MyDrive/DL Final Project/' 
BASE_PATH = '/gdrive/My Drive/CSE 490G1543/DL Final Project/'
DATA_PATH = BASE_PATH + 'German/'

os.chdir(BASE_PATH)
os.chdir(DATA_PATH)
!pwd
!ls

os.chdir('/content')

import torch
import torch.nn as nn
from torchvision import datasets
from torchvision import transforms
from torchvision import models
import numpy as np
import os
import torch.nn.functional as F
import torch.optim as optim
import h5py
import sys
import matplotlib.pyplot as plt
sys.path.append(BASE_PATH)
import seaborn as sns
# sns.set_theme()
import pt_util

# Data loader
class H5Dataset(torch.utils.data.Dataset):
    def __init__(self, data_dir='/gdrive/My Drive/CSE 490G1543/DL Final Project/German/', mode='train', transform=None):
        h5_string = ''
        if mode == 'train':
          h5_string = 'Train.h5'
        else:
          h5_string = 'Test.h5'
        
        self.transform = transform
        temp = os.path.join(data_dir, h5_string)
        self.h5_file = h5py.File(temp, 'r')
        self.images = self.h5_file['Data'][:]
        self.labels = torch.LongTensor(self.h5_file['Labels'][:])
        
    def __len__(self):
        return self.images.shape[0]
      
    def __getitem__(self, idx):
        data = self.images[idx]
        label = self.labels[idx]
        
        if self.transform:
            data = self.transform(data)
        return (data.type(torch.FloatTensor), label)

transform_train = transforms.Compose([
    transforms.ToTensor()
])

transform_test = transforms.Compose([
    transforms.ToTensor()
])

def get_activation(name):
    def hook(model, input, output):
        activation[name] = output.detach()
    return hook

class TheNet(nn.Module):
  def __init__(self, out_size):
    super(TheNet, self).__init__()
    self.net = models.vgg19_bn(pretrained=True)
    self.fc = nn.Linear(1000, out_size)
    self.accuracy = None
  
    features = list(models.vgg19_bn(pretrained = True).features)[:]
    self.features = nn.ModuleList(features).eval() 

  def forward(self, x):

    x1 = self.net(x)
    x2 = self.fc(x1)

    results = []
    for ii,model in enumerate(self.features):
        x = model(x)
        results.append(x)

    return x2, results

  def loss(self, prediction, label, reduction='mean'):
    loss_val = F.cross_entropy(prediction, label.squeeze(), reduction=reduction)
    return loss_val

import time

def train(model, device, train_loader, optimizer, epoch, log_interval):
  model.train()
  losses = []
  for batch_idx, (data, label) in enumerate(train_loader):
    data, label = data.to(device), label.to(device)
    optimizer.zero_grad()
    output, _ = model(data)
    loss = model.loss(output, label)
    losses.append(loss.item())
    loss.backward()
    optimizer.step()
    if batch_idx % log_interval == 0:
      print('{} Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
          time.ctime(time.time()),
          epoch, batch_idx * len(data), len(train_loader.dataset),
          100. * batch_idx / len(train_loader), loss.item()))
  return np.mean(losses)

def test(model, device, test_loader, log_interval=None):
  model.eval()
  test_loss = 0
  correct = 0

  with torch.no_grad():
    for batch_idx, (data, label) in enumerate(test_loader):
      data, label = data.to(device), label.to(device)
      output, _ = model(data)
      test_loss_on = model.loss(output, label, reduction='sum').item()
      test_loss += test_loss_on
      pred = output.max(1)[1]
      correct_mask = pred.eq(label.view_as(pred))
      num_correct = correct_mask.sum().item()
      correct += num_correct
      if log_interval is not None and batch_idx % log_interval == 0:
        print('{} Test: [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
            time.ctime(time.time()),
            batch_idx * len(data), len(test_loader.dataset),
            100. * batch_idx / len(test_loader), test_loss_on))
        
  test_loss /= len(test_loader.dataset)
  test_accuracy = 100. * correct / len(test_loader.dataset)
  print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
          test_loss, correct, len(test_loader.dataset), test_accuracy))
  return test_loss, test_accuracy

from copy import deepcopy
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

def prune(model, data, d_labels, layer_indices, prune_method="l2", prune_ratio=0.5):
    pruned_model = deepcopy(model)
    if prune_ratio == 1:
        return pruned_model

    if prune_method != "kmeans":
        out, results = model.forward(data)

    if prune_method == "gradient":
        loss = model.loss(out, d_labels)
        loss.backward()

    state_dict = pruned_model.state_dict()

    for idx in layer_indices:
        
        # Keys for the state dict
        key_w = "net.features." + str(idx) + ".weight"
        key_b = "net.features." + str(idx) + ".bias"

        # Find indices based on pruning method
        if prune_method == "l2" or prune_method == "hrank":  # label-free
            # Get activations
            activations = results[idx].detach().numpy()
            activations = np.maximum(activations, 0)
            k = int(activations.shape[1] * (1-prune_ratio))

            if prune_method == "l2":
                # Get the l2-norm of the n x w x h vector that belongs to a single filter
                activations = np.reshape(activations, (activations.shape[1], -1))
                norms = np.linalg.norm(activations, axis=1)

                # Prune the k lowest-norm filters
                indices = norms.argsort()[:k]

            else:  # prune_method == "hrank"
                # Create an empty ranks matrix of n x num_filters
                ranks = np.zeros((activations.shape[0], activations.shape[1])) # 2048, 64
                
                # Calculate the rank of each output
                for filter_idx in range(activations.shape[1]):
                    for sample_idx in range(activations.shape[0]):
                        ranks[sample_idx,filter_idx] = np.linalg.matrix_rank(activations[sample_idx, filter_idx, :, :])
                
                # Average the ranks, collapsing the batch dimension (n)
                ranks = np.mean(ranks, axis=0)

                # Prune the k lowest-average-rank filters
                indices = ranks.argsort()[:k]

        elif prune_method == "kmeans":  # data-free
            # Get filters
            filters = state_dict[key_w].detach().numpy()
            filters = np.reshape(filters, (filters.shape[0], -1))
            
            # Perform kmeans clustering on the filters
            k = int(prune_ratio * filters.shape[0])
            kmeans = KMeans(n_clusters=k, random_state=0).fit(filters)

            centroids = kmeans.cluster_centers_
            labels = kmeans.labels_
            indices = []

            # Find representative filters that are closest to the centroids.
            # We are NOT using the centroids themselves as filters
            for i in range(centroids.shape[0]):
                curr_indices = np.where(labels == i)[0]
                diff = np.linalg.norm(filters[curr_indices] - centroids[i], axis=1)
                to_prune = diff.argsort()[1:]
                indices.extend(currr_indices[to_prune])

        else:  # label-dependent (gradient)
            # Get the filters
            filters = state_dict[key_w].detach().numpy() 
            # Get the gradients
            grad = model.net.features[idx].weight.grad.numpy()
            # Multiply the gradients with the filters
            scores = np.abs(grad * filters)
            scores = np.reshape(scores, (scores.shape[0], -1))

            # Calculate the sizes (norms) of each filter x gradient "score"
            scores = np.linalg.norm(scores, axis=1)

            k = int(filters.shape[0] * (1-prune_ratio))

            # Prune the k lowest-score filters
            indices = scores.argsort()[:k]

        # Perform the pruning for indices found
        pruned_model.state_dict()[key_w][indices,:,:,:] = 0
        pruned_model.state_dict()[key_b][indices] = 0
        
        # Zeroing out the same batchnorm parameters 
        key_w_bn = "net.features." + str(idx + 1) + ".weight"
        key_b_bn = "net.features." + str(idx + 1) + ".bias"
        key_mu_bn = "net.features." + str(idx + 1) + ".running_mean"
        key_sig_bn = "net.features." + str(idx + 1) + ".running_var"
        pruned_model.state_dict()[key_w_bn][indices] = 0
        pruned_model.state_dict()[key_b_bn][indices] = 0
        pruned_model.state_dict()[key_mu_bn][indices] = 0
        pruned_model.state_dict()[key_sig_bn][indices] = 0

    return pruned_model

def prune_experiment(original_model, prune_type, single_batch, single_lab, ratios, exp_num):

    vgg11_conv_idx = [0,3,6,8,11,13,16,18]
    vgg19_conv_idx = [0, 3, 7, 10, 14, 17, 20, 23, 27, 30, 33, 36, 40, 43, 46, 49]

    pruning_accs = []

    for ratio in ratios:
        
        print("---------------------------------- " + prune_type + " " + str(ratio) + " ----------------------------------")

        pruned_model = prune(original_model, single_batch, single_lab, vgg19_conv_idx, prune_type, ratio)
        
        # Training hyperparameters
        BATCH_SIZE = 16
        TEST_BATCH_SIZE = 10
        EPOCHS = 2
        LEARNING_RATE = 0.001
        MOMENTUM = 0.9
        USE_CUDA = True
        PRINT_INTERVAL = 10000
        WEIGHT_DECAY = 0.0005

        EXPERIMENT_VERSION = str(exp_num + ratio) #"1.2"
        LOG_PATH = DATA_PATH + 'logs/' + EXPERIMENT_VERSION + '/'

        use_cuda = USE_CUDA and torch.cuda.is_available()

        device = torch.device("cuda" if use_cuda else "cpu")
        print('Using device', device)
        import multiprocessing
        print('num cpus:', multiprocessing.cpu_count())

        kwargs = {'num_workers': multiprocessing.cpu_count(),
                  'pin_memory': True} if use_cuda else {}

        train_loader = torch.utils.data.DataLoader(H5Dataset(DATA_PATH, 'train', transform=transform_train), batch_size=BATCH_SIZE, shuffle=True)
        test_loader = torch.utils.data.DataLoader(H5Dataset(DATA_PATH, 'test', transform=transform_train), batch_size=BATCH_SIZE, shuffle=False)

        # return
        model = pruned_model.to(device)
        optimizer = optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=MOMENTUM, weight_decay=WEIGHT_DECAY)
        start_epoch = 0

        train_losses, test_losses, test_accuracies = pt_util.read_log(LOG_PATH + 'log.pkl', ([], [], []))
        test_loss, test_accuracy = test(model, device, test_loader)

        test_losses.append((start_epoch, test_loss))
        test_accuracies.append((start_epoch, test_accuracy))

        model = model.cpu()
        for param_tensor in model.state_dict():
            print("number of nonzero filters: " + str(model.state_dict()[param_tensor].sum(dim=(1, 2, 3)).count_nonzero()))
            break
        model = model.to(device)
        try:
          for epoch in range(start_epoch, EPOCHS + 1):
            train_loss = train(model, device, train_loader, optimizer, epoch, PRINT_INTERVAL)
            test_loss, test_accuracy = test(model, device, test_loader)
            test_accuracies.append((epoch, test_accuracy))
            model = model.cpu()
            for param_tensor in model.state_dict():
                print("number of nonzero filters: " + str(model.state_dict()[param_tensor].sum(dim=(1, 2, 3)).count_nonzero()))
                break
            model = model.to(device)
        except KeyboardInterrupt as ke:
          print('Interrupted')
        except:
          import traceback
          traceback.print_exc()
        finally:
          pruning_accs.append(test_accuracies[-1][1])
    return pruning_accs

torch.manual_seed(0)
original_model = TheNet(out_size=43)
prune_loader = torch.utils.data.DataLoader(H5Dataset(DATA_PATH, 'train', transform=transform_train), batch_size=512, shuffle=True)
single_batch,single_lab = next(iter(prune_loader))

pruning_ratios = [0.75, 0.5, 0.25, .2, 0.15, 0.1, 0.05, 0.01]

baseline_accuracy = prune_experiment(original_model, "l2", single_batch, single_lab, [1], 10)
print("BASELINE ACCURACY:")
print(baseline_accuracy)

grad_accuracies = prune_experiment(original_model, "gradient", single_batch, single_lab, pruning_ratios, 10)
print("GRAD BASED PRUNING ACCURACY:")
print(grad_accuracies)

l2_accuracies = prune_experiment(original_model, "l2", single_batch, single_lab, pruning_ratios, 11)
print("L2 PRUNING ACCURACY:")
print(l2_accuracies)

hrank_accuracies = prune_experiment(original_model, "hrank", single_batch, single_lab, pruning_ratios, 12)
print("HRANK PRUNING ACCURACY:")
print(hrank_accuracies)

kmeans_accuracies = prune_experiment(original_model, "kmeans", single_batch, single_lab, pruning_ratios, 13)
print("KMEANS PRUNING ACCURACY:")
print(kmeans_accuracies)