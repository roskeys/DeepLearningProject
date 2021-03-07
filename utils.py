from os import listdir
# Matplotlib
import matplotlib.pyplot as plt
# Numpy
import numpy as np
# Pillow
from PIL import Image
# Torch
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import transforms


class Lung_Dataset(Dataset):
    def __init__(self, groups):
        """
        Constructor for generic Dataset class - simply assembles
        the important parameters in attributes.
        """
        assert groups in {'train', 'test', 'val'}, "groups must be either 'train', 'test' or 'val'"
        self.groups = groups
        # All images are of size 150 x 150
        self.img_size = (150, 150)
        # Only two classes will be considered here (normal and infected)
        self.classes = {'normal': 0, 'non-covid': 1, 'covid': 2}

        # Path to images for different parts of the dataset
        self.dataset_paths = {
            'normal': f'./dataset/{groups}/normal/',
            'non-covid': f'./dataset/{groups}/infected/non-covid/',
            'covid': f'./dataset/{groups}/infected/covid/'
        }
        # Number of images in each part of the dataset
        self.dataset_numbers = {
            'normal': len(listdir(self.dataset_paths['normal'])),
            'non-covid': len(listdir(self.dataset_paths['non-covid'])),
            'covid': len(listdir(self.dataset_paths['covid'])),
        }

    def describe(self):
        """
        Descriptor function.
        Will print details about the dataset when called.
        """
        # Generate description
        msg = "This is the dataset of the Lung Dataset"
        msg += " used for the Small Project Demo in the 50.039 Deep Learning class"
        msg += " in Feb-March 2021. \n"
        msg += "It contains a total of {} images, ".format(sum(self.dataset_numbers.values()))
        msg += "of size {} by {}.\n".format(self.img_size[0], self.img_size[1])
        msg += "The images are stored in the following locations "
        msg += "and each one contains the following number of images:\n"
        for key, val in self.dataset_paths.items():
            msg += " - {}, in folder {}: {} images.\n".format(key, val, self.dataset_numbers[key])
        print(msg)

    def open_img(self,  class_val, index_val):
        """
        Opens image with specified parameters.
        Parameters:
        - group_val should take values in 'train', 'test' or 'val'.
        - class_val variable should be set to 'normal' or 'infected'.
        - index_val should be an integer with values between 0 and the maximal number of images in dataset.
        Returns loaded image as a normalized Numpy array.
        """
        # # Asserts checking for consistency in passed parameters
        # err_msg = "Error - group_val variable should be set to 'train', 'test' or 'val'."
        # assert group_val in self.groups, err_msg

        err_msg = "Error - class_val variable should be set to 'normal', 'non-covid' and 'covid'"
        assert class_val in self.classes.keys(), err_msg

        max_val = self.dataset_numbers[class_val]
        err_msg = "Error - index_val variable should be an integer between 0 and the maximal number of images."
        err_msg += "\n(In {}/{}, you have {} images.)".format(self.groups, class_val, max_val)
        assert isinstance(index_val, int), err_msg
        assert 0 <= index_val <= max_val, err_msg

        # Open file as before
        path_to_file = '{}/{}.jpg'.format(self.dataset_paths[class_val], index_val)
        with open(path_to_file, 'rb') as f:
            im = np.asarray(Image.open(f)) / 255.
        f.close()
        return im

    def show_img(self, class_val, index_val):
        """
        Opens, then displays image with specified parameters.

        Parameters:
        - group_val should take values in 'train', 'test' or 'val'.
        - class_val variable should be set to 'normal' or 'infected'.
        - index_val should be an integer with values between 0 and the maximal number of images in dataset.
        """

        # Open image
        im = self.open_img(class_val, index_val)

        # Display
        plt.imshow(im)

    def __len__(self):
        """
        Length special method, returns the number of images in dataset.
        """

        # Length function
        return sum(self.dataset_numbers.values())

    def __getitem__(self, index):
        """
        Getitem special method.
        Expects an integer value index, between 0 and len(self) - 1.
        Returns the image and its label as a one hot vector, both
        in torch tensor format in dataset.
        """
        # Get item special method
        normal_range = self.dataset_numbers['normal']
        non_covid_range = self.dataset_numbers['non-covid'] + normal_range
        covid_range = self.dataset_numbers['covid'] + non_covid_range

        index = index % covid_range
        # self.classes = {'normal': 0, 'non-covid': 1, 'covid': 2}
        if 0 <= index < normal_range:
            class_val = 'normal'
            label = torch.Tensor([1, 0, 0])
        elif normal_range <= index < non_covid_range:
            class_val = 'non-covid'
            label = torch.Tensor([0, 1, 0])
            index = index - normal_range
        elif non_covid_range <= index < covid_range:
            class_val = 'covid'
            label = torch.Tensor([0, 0, 1])
            index = index - non_covid_range
        else:
            raise ValueError("Index larger than the max index")
        im = self.open_img(class_val, index)
        im = transforms.functional.to_tensor(np.array(im)).float()
        return im, label


