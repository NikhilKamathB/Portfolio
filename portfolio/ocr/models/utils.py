import torch
import torch.nn as nn
import torch.nn.init as init
from torchvision import models
from collections import namedtuple


def freeze(model: object) -> None:
    '''
        This function freezes the model.
        Input params: None
        Returns: None.
    '''
    for _, param in model.named_parameters():
        param.requires_grad = False


class InitializeModule:

    '''
        This class initalizes weights of the given module.
        Supports -> nn.Conv2d, nn.BatchNorm2d and nn.Linear
        Other modules may be added in similar way.
        Initialization is done using methods offered in torch.nn.init.
        Params are set to defaults.
    '''

    def __init__(self) -> None:
        '''
            Input params: `modules` - an nn instance.
            Returns: `None`.
        '''
        self.initialization_map = {
            "conv2d": "xavier_normal_weights",
            "conv2d_bias": "zero_bias",
            "batchnorm2d": "ones_weights",
            "batchnorm2d_bias": "zero_bias",
            "linear": "xavier_uniform_weights",
            "linear_bias": "zero_bias"
        }
    
    def zero_bias(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        module.bias.data.zero_()
    
    def uniform_bias(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.uniform_(module.bias.data)
    
    def normal_bias(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.normal_(module.bias.data)
    
    def ones_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.ones_(module.weight.data)

    def uniform_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.uniform_(module.weight.data)
    
    def normal_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.normal_(module.weight.data)
    
    def xavier_uniform_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.xavier_uniform_(module.weight.data)
    
    def xavier_normal_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.xavier_normal_(module.weight.data)
    
    def kaiming_uniform_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.kaiming_uniform_(module.weight.data)
    
    def kaiming_normal_weights(self, module: object) -> None:
        '''
            Input params: `module` - an nn instance.
            Returns: `None`.
        '''
        init.kaiming_normal_(module.weight.data)
    
    def initialize_weights(self, key: str, module: object) -> None:
        '''
            Input params: `key` - a string representing initialization method.
                          `module` - an nn instance.
            Returns: `None`.
        '''
        if self.initialization_map[key] == "ones_weights":
            self.ones_weights(module)
        elif self.initialization_map[key] == "uniform_weights":
            self.uniform_weights(module)
        elif self.initialization_map[key] == "normal_weights":
            self.normal_weights(module)
        elif self.initialization_map[key] == "xavier_uniform_weights":
            self.xavier_uniform_weights(module)
        elif self.initialization_map[key] == "xavier_normal_weights":
            self.xavier_normal_weights(module)
        elif self.kaiming_uniform_weights[key] == "kaiming_uniform_weights":
            self.kaiming_uniform_weights(module)
        elif self.kaiming_normal_weights[key] == "kaiming_normal_weights":
            self.kaiming_normal_weights(module)
        else:
            self.xavier_normal_weights(module)
        
    def initialize_bias(self, key: str, module: object) -> None:
        '''
            Input params: `key` - a string representing initialization method.
                          `module` - an nn instance.
            Returns: `None`.
        '''
        if self.initialization_map[key] == "zero_bias":
            self.zero_bias(module)
        elif self.initialization_map[key] == "uniform_bias":
            self.uniform_bias(module)
        elif self.initialization_map[key] == "normal_bias":
            self.normal_bias(module)
        else:
            self.zero_bias(module)

    def initialize(self, initialization_map: dict = {}, modules: object = None, verbose: bool = False) -> None:
        '''
            Input params: `None`.
            Returns: `None`.
        '''
        assert modules is not None, "Modules cannot be None."
        self.modules = modules
        for module in self.modules:
            if isinstance(module, nn.Conv2d):
                if "conv2d" in initialization_map.keys():
                    self.initialization_map["conv2d"] = initialization_map["conv2d"]
                    self.initialize_weights("conv2d", module)
                else:
                    self.xavier_normal_weights(module)
                if module.bias is not None:
                    if "conv2d_bias" in initialization_map.keys():
                        self.initialization_map["conv2d_bias"] = initialization_map["conv2d_bias"]
                        self.initialize_bias("conv2d_bias", module)
                    else:
                        self.zero_bias(module)
            elif isinstance(module, nn.BatchNorm2d):
                if "batchnorm2d" in initialization_map.keys():
                    self.initialization_map["batchnorm2d"] = initialization_map["batchnorm2d"]
                    self.initialize_weights("batchnorm2d", module)
                else:
                    self.ones_weights(module)
                if module.bias is not None:
                    if "batchnorm2d_bias" in initialization_map.keys():
                        self.initialization_map["batchnorm2d_bias"] = initialization_map["batchnorm2d_bias"]
                        self.initialize_bias("batchnorm2d_bias", module)
                    else:
                        self.zero_bias(module)
            elif isinstance(module, nn.Linear):
                if "linear" in initialization_map.keys():
                    self.initialization_map["linear"] = initialization_map["linear"]
                    self.initialize_weights("linear", module)
                else:
                    self.xavier_normal_weights(module)
                if module.bias is not None:
                    if "linear_bias" in initialization_map.keys():
                        self.initialization_map["linear_bias"] = initialization_map["linear_bias"]
                        self.initialize_bias("linear_bias", module)
                    else:
                        self.zero_bias(module)
            else:
                if verbose:
                    print("Warning! Skipping as module not supported for initialization. Please add it to the `InitializeWeights` class.")
                    print("Module: ", module)


class DoubleConv2d(nn.Module):

    '''
        A class that implements a 2D double convolutional layer.
    '''

    def __init__(self, in_channels: int, mid_channels: int, out_channels: int) -> None:
        '''
            Intial definition for the DoubleConv2d.
            Input params: `in_channels` - an integer representing the number of input channels.
                          `mid_channels` - an integer representing the number of intermediate channels.
                          `out_channels` - an integer representing the number of output channels.
            Returns: `None`.
        '''
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels + mid_channels, mid_channels, kernel_size=1),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        '''
            Input params: `x` - a tensor of shape (batch_size, in_channels, height, width).
            Returns: `x` - a tensor of shape (batch_size, out_channels, height, width).
        '''
        return self.conv(x)


class VGG16_BN(torch.nn.Module):

    '''
        Custom VGG-16 with batch normalization.
    '''

    def __init__(self, freeze: bool = True) -> None:
        '''
            Initial definitions for the VGG-16 model.
            Input params: `freeze` - a boolean value indicating whether to freeze
                                     weights of first block.
            Returns: `None`.

        '''
        super().__init__()
        initialize_module = InitializeModule()
        vgg16_bn_features = models.vgg16_bn(weights="VGG16_BN_Weights.DEFAULT").features
        self.slice1 = nn.Sequential()
        self.slice2 = nn.Sequential()
        self.slice3 = nn.Sequential()
        self.slice4 = nn.Sequential()
        for i in range(13):
            self.slice1.add_module(f"{str(i)}", vgg16_bn_features[i])
        for i in range(13, 20):
            self.slice2.add_module(f"{str(i)}", vgg16_bn_features[i])
        for i in range(20, 30):
            self.slice3.add_module(f"{str(i)}", vgg16_bn_features[i])
        for i in range(30, 40):
            self.slice4.add_module(f"{str(i)}", vgg16_bn_features[i])
        self.slice5 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(in_channels=512, out_channels=1024, kernel_size=3, padding=6, dilation=6),
            nn.Conv2d(in_channels=1024, out_channels=1024, kernel_size=1),
        )
        initialize_module.initialize(modules=self.slice5.modules())
        if freeze:
            for param in self.slice1.parameters():
                param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> namedtuple:
        '''
            Input params: `x` - a tensor of shape (batch_size, channels, height, width).
            Returns: `x` - a tensor of shape (batch_size, channels, height, width).
        '''
        slice1_out = self.slice1(x)
        slice2_out = self.slice2(slice1_out)
        slice3_out = self.slice3(slice2_out)
        slice4_out = self.slice4(slice3_out)
        slice5_out = self.slice5(slice4_out)
        vgg16_bn_output = namedtuple('VGG16_BN_OUTPUT', ['slice1_out', 'slice2_out', 'slice3_out', 'slice4_out', 'slice5_out'])
        return vgg16_bn_output(slice1_out, slice2_out, slice3_out, slice4_out, slice5_out)