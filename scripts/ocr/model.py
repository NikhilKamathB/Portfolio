import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from collections import namedtuple, OrderedDict
from transformers import ViTModel, ViTConfig, \
                        TrOCRForCausalLM, TrOCRConfig, \
                        VisionEncoderDecoderModel, TrOCRProcessor

OCR_TEXT_RECOGNITION_PROCESSOR_MODEL = "microsoft/trocr-base-handwritten"

def freeze(model: object) -> None:
    '''
        This function freezes the model.
        Input params: None
        Returns: None.
    '''
    for _, param in model.named_parameters():
        param.requires_grad = False


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
        vgg16_bn_features = models.vgg16_bn(weights=None).features
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
    

class CRAFT(nn.Module):

    '''
        CRAFT model.
    '''

    def __init__(self, freeze: bool = True) -> None:
        '''
            Initial defintions for the CRAFT model.
            Input params: 
                `freeze` - a boolean value to freeze the model.
            Returns: `None`.
        '''
        super().__init__()
        self.basenet = VGG16_BN(freeze=freeze)
        self.upconv1 = DoubleConv2d(in_channels=1024, mid_channels=512, out_channels=256)
        self.upconv2 = DoubleConv2d(in_channels=512, mid_channels=256, out_channels=128)
        self.upconv3 = DoubleConv2d(in_channels=256, mid_channels=128, out_channels=64)
        self.upconv4 = DoubleConv2d(in_channels=128, mid_channels=64, out_channels=32)
        self.conv_cls = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=32, out_channels=16, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=16, out_channels=16, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=16, out_channels=2, kernel_size=1)
        )
    
    def forward(self, x: torch.Tensor) -> tuple:
        '''
            Input params: `x` - a tensor of shape (batch_size, channels, height, width).
            Returns: `x` - a tensor of shape (batch_size, channels, height, width).
        '''
        slice_1_out, slice_2_out, slice_3_out, slice_4_out, slice_5_out = self.basenet(x)
        out = self.upconv1(torch.cat((slice_5_out, slice_4_out), dim=1))
        out = F.interpolate(out, size=slice_3_out.size()[2:], mode='bilinear', align_corners=False)
        out = self.upconv2(torch.cat((out, slice_3_out), dim=1))
        out = F.interpolate(out, size=slice_2_out.size()[2:], mode='bilinear', align_corners=False)
        out = self.upconv3(torch.cat((out, slice_2_out), dim=1))
        out = F.interpolate(out, size=slice_1_out.size()[2:], mode='bilinear', align_corners=False)
        feature = self.upconv4(torch.cat((out, slice_1_out), dim=1))
        out = self.conv_cls(feature)
        return (out.permute(0, 2, 3, 1), feature)


class CRAFTModel:

    '''
        CRAFTModel class is used to do model inferencing.
    '''

    def __init__(self,
                 saved_model: str = None,
                 raw_load: bool = True) -> None:
        '''
            Initial definition for the OCRModel class.
            Input params:
                device - a string representing the device to use.
                saved_model - a string representing the path to the saved model.
                raw_load - a boolean value to load the model in raw format.
            Returns: None.
        '''
        self.device = "cpu"
        self.saved_model = saved_model
        self.raw_load = raw_load
        self.model = self.load_torch_model()
    
    def load_torch_model(self) -> object:
        '''
            This function loads a torch model.
            Input params: None
            Returns: a model object.
        '''
        model = CRAFT(freeze=True)
        if self.saved_model is not None:
            state_dict = torch.load(self.saved_model, map_location=torch.device(self.device))
            if self.raw_load:
                start_idx = 0
                new_state_dict = OrderedDict()
                if list(state_dict.keys())[0].startswith("module"):
                    start_idx = 1
                for k, v in state_dict.items():
                    name = ".".join(k.split(".")[start_idx: ])
                    new_state_dict[name] = v
                state_dict = new_state_dict
                model.load_state_dict(state_dict)
            else:
                model.load_state_dict(state_dict["model_state_dict"])
            model.to(self.device)
            freeze(model=model)
        return model


class TrOCR:

    def __init__(self, 
                 pretrained: bool = True,
                 pretrained_path: str = OCR_TEXT_RECOGNITION_PROCESSOR_MODEL,
                 device: str = "cpu",
                 processor: object = None,
                 processor_pretrained_path: str = OCR_TEXT_RECOGNITION_PROCESSOR_MODEL,
                 max_length: int = 64,
                 early_stopping: bool = True,
                 no_repeat_ngram_size: int = 3,
                 length_penalty: float = 2.0,
                 num_beams: int = 4,
                ) -> None:
        '''
            Initializes the TrOCR model.
            Input params:
                pretrained: bool -> Whether to use a pretrained model or not.
                pretrained_path: str -> The path to the pretrained model.
                device: str -> The device to use for training.
                processor: object -> The processor to use for the model.
                processor_pretrained_path: str -> The path to the pretrained processor.
                max_length: int -> The maximum length of the sequence.
                early_stopping: bool -> Whether to use early stopping or not.
                no_repeat_ngram_size: int -> The size of the ngram to avoid repetition.
                length_penalty: float -> The length penalty to use for beam search.
                num_beams: int -> The number of beams to use for beam search.
        '''
        encoder = ViTModel(ViTConfig())
        decoder = TrOCRForCausalLM(TrOCRConfig())
        if pretrained:
            self.model = VisionEncoderDecoderModel.from_pretrained(pretrained_path)
        else:
            self.model = VisionEncoderDecoderModel(encoder=encoder, decoder=decoder)
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        self.processor = processor if processor is not None else TrOCRProcessor.from_pretrained(processor_pretrained_path)
        self.max_length = max_length
        self.early_stopping = early_stopping
        self.no_repeat_ngram_size = no_repeat_ngram_size
        self.length_penalty = length_penalty
        self.num_beams = num_beams
        self.config()
        self.model.to(self.device)

    def config(self) -> None:
        '''
            Configures the model.
        '''
        # declaration of special token
        self.model.config.decoder_start_token_id = self.processor.tokenizer.cls_token_id
        self.model.config.pad_token_id = self.processor.tokenizer.pad_token_id
        # declaration of vocabulary size
        self.model.config.vocab_size = self.model.config.decoder.vocab_size
        # declaration of beam search
        self.model.config.eos_token_id = self.processor.tokenizer.eos_token_id
        self.model.config.max_length = self.max_length
        self.model.config.early_stopping = self.early_stopping
        self.model.config.no_repeat_ngram_size = self.no_repeat_ngram_size
        self.model.config.length_penalty = self.length_penalty
        self.model.config.num_beams = self.num_beams

class TrOCRModel:

    '''
        TrOCRModel class is used to do model inferencing.
    '''

    def __init__(self,
                 saved_model: str = None) -> None:
        '''
            Initial definition for the OCRModel class.
            Input params:
                device - a string representing the device to use.
                saved_model - a string representing the path to the saved model.
            Returns: None.
        '''
        self.device = "cpu"
        self.saved_model = saved_model if saved_model is not None else OCR_TEXT_RECOGNITION_PROCESSOR_MODEL
        self.model = self.load_torch_model()
    
    def load_torch_model(self) -> object:
        '''
            This function loads a torch model.
            Input params: None
            Returns: a model object.
        '''
        model = TrOCR(device=self.device, pretrained=self.saved_model).model
        freeze(model=model)
        return model