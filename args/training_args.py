from dataclasses import dataclass, field
from typing import Optional

from transformers import TrainingArguments, Seq2SeqTrainingArguments

from consts import *


@dataclass
class ProjectSeq2SeqTrainingArguments(Seq2SeqTrainingArguments):
    metrics: str = field(
        default='gleu,rouge,blue,sacrebleu,bertscore,meteor',
        metadata={"help": "Names of huggingface metrics you would like to compute seperated by commas (e.g accuracy,f1). "
                          "Notice that by default the metrics receives only predictions and labels, "
                          "for specific behavior refer to utils.train_utils.get_compute_metrics."}
    )
    freeze_embeds: bool = field(
        default=False,
        metadata={"help": "Freeze embeddings during training"}
    )

    def __post_init__(self):
        super().__post_init__()
        if self.metrics is not None:
            self.metrics = self.metrics.split(',')


