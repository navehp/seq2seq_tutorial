from transformers import Trainer

from torch import nn


class CustomTrainer(Trainer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kl_loss_func = nn.KLDivLoss(reduction="batchmean")

    def compute_loss(self, model, inputs, return_outputs=False, return_embeddings=False):
        target_p = inputs["labels"]
        outputs = model(inputs["input_ids"], attention_mask=inputs["attention_mask"], output_hidden_states=return_embeddings)
        logits = outputs[0]
        loss = self.kl_loss_func(logits.log_softmax(dim=-1), target_p)

        if return_outputs:
            return loss, outputs

        return loss