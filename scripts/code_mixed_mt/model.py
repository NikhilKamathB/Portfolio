import torch
from transformers import BartConfig
from transformers import BartForConditionalGeneration as BartModelGen


MBART_MODEL_CONDITIONAL_GENERATION_VOCAB = 50265


class BartForConditionalGeneration:

    def __init__(self,
                 pretrained: bool = True,
                 pretrained_path: str = "facebook/bart-large",
                 device: str = "cpu") -> None:
        '''
            Initializes the BartForConditionalGeneration model.
            Input params:
                pretrained: bool -> Whether to use a pretrained model or not.
                pretrained_path: str -> The path to the pretrained model.
                device: str -> The device to use for training.
        '''
        if pretrained:
            self.model = BartModelGen.from_pretrained(pretrained_path)
        else:
            self.model = BartModelGen(
                BartConfig(
                    vocab_size=MBART_MODEL_CONDITIONAL_GENERATION_VOCAB
                )
            )
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        self.config()
        self.model.to(self.device)

    def config(self) -> None:
        '''
            Configures the model.
        '''
        self.model.config.vocab_size = MBART_MODEL_CONDITIONAL_GENERATION_VOCAB