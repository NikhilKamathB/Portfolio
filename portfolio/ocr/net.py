import torch
from collections import OrderedDict
from ocr.models.craft import CRAFT
from ocr.models.trocr import TrOCR
from ocr.models.utils import *


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
        self.saved_model = saved_model
        self.model = self.load_torch_model()
    
    def load_torch_model(self) -> object:
        '''
            This function loads a torch model.
            Input params: None
            Returns: a model object.
        '''
        model = TrOCR(device=self.device).model
        if self.saved_model is not None:
            state_dict = torch.load(self.saved_model, map_location=torch.device("cpu"))
            model.load_state_dict(state_dict["model_state_dict"])
            model.to(self.device)
        freeze(model=model)
        return model