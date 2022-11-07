#!/usr/bin/env python
# coding=utf-8
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Finetuning the library models for sequence classification on GLUE."""
# You can also adapt this script on your own text classification task. Pointers for this are left as comments.

import logging
import os
import random
import sys

import torch
from transformers import (
    AutoConfig,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    HfArgumentParser,
    Seq2SeqTrainer,
    default_data_collator,
    set_seed,
)
from transformers.utils.versions import require_version

from consts import *
from modeling import *
from args.data_args import DataTrainingArguments
from args.model_args import ModelArguments
from args.training_args import ProjectSeq2SeqTrainingArguments
from utils.utils import *
from utils.data_utils import *
from utils.train_utils import *


# Will error if the minimal version of Transformers is not installed. Remove at your own risks.
# check_min_version("4.16.0.dev0")

require_version("datasets>=1.8.0", "To fix: pip install -r examples/pytorch/text-classification/requirements.txt")

logger = logging.getLogger(__name__)


def preprocess_datasets(data_args, model_args, training_args, raw_datasets):

    # Load pretrained model and tokenizer
    config = AutoConfig.from_pretrained(
        model_args.config_name if model_args.config_name else model_args.model_name_or_path,
        finetuning_task=data_args.dataset,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
    )

    if data_args.max_seq_length > tokenizer.model_max_length:
        logger.warning(
            f"The max_seq_length passed ({data_args.max_seq_length}) is larger than the maximum length for the"
            f"model ({tokenizer.model_max_length}). Using max_seq_length={tokenizer.model_max_length}."
        )
    max_seq_length = min(data_args.max_seq_length, tokenizer.model_max_length)

    def preprocess_function(examples):
        # Tokenize the texts
        result = tokenizer(examples['document'], padding=data_args.padding, max_length=max_seq_length, truncation=True)
        with tokenizer.as_target_tokenizer():
            tokenized_targets = \
                tokenizer(examples['summary'], padding=data_args.padding, max_length=max_seq_length, truncation=True)[INPUT_IDS]
            result[LABELS] = tokenized_targets
        return result

    with training_args.main_process_first(desc="dataset map pre-processing"):
        tokenized_datasets = raw_datasets.map(
            preprocess_function,
            batched=True,
            desc="Running tokenizer on dataset",
        )
    return tokenized_datasets


def train_model(data_args, model_args, training_args, raw_datasets):

    # Load pretrained model and tokenizer
    config = AutoConfig.from_pretrained(
        model_args.config_name if model_args.config_name else model_args.model_name_or_path,
        finetuning_task=data_args.dataset,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_args.model_name_or_path,
        from_tf=bool(".ckpt" in model_args.model_name_or_path),
        config=config,
    )
    if training_args.freeze_embeds:
        freeze_embeds(model)

    # Make sure datasets are here and select a subset if specified
    if training_args.do_train:
        if TRAIN not in raw_datasets:
            raise ValueError("--do_train requires a train dataset")
        train_dataset = raw_datasets[TRAIN]
        if data_args.max_train_samples is not None:
            train_dataset = train_dataset.shuffle(training_args.seed).select(range(data_args.max_train_samples))

    if training_args.do_eval:
        if VALIDATION not in raw_datasets:
            raise ValueError("--do_eval requires a validation dataset")
        eval_dataset = raw_datasets[VALIDATION]
        if data_args.max_eval_samples is not None:
            eval_dataset = eval_dataset.shuffle(training_args.seed).select(range(data_args.max_eval_samples))

    if training_args.do_predict:
        if TEST not in raw_datasets:
            raise ValueError("--do_predict requires a test dataset")
        predict_dataset = raw_datasets[TEST]
        if data_args.max_predict_samples is not None:
            predict_dataset = predict_dataset.shuffle(training_args.seed).select(range(data_args.max_predict_samples))

    # Log a few random samples from the training set:
    if training_args.do_train:
        for index in random.sample(range(len(train_dataset)), 3):
            logger.info(f"Sample {index} of the training set: {train_dataset[index]}.")

    compute_metrics = get_compute_metrics(tokenizer, training_args.metrics)

    # Initialize our Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset if training_args.do_train else None,
        eval_dataset=eval_dataset if training_args.do_eval else None,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )

    # Training
    if training_args.do_train:
        train_result = trainer.train()
        metrics = train_result.metrics
        max_train_samples = (
            data_args.max_train_samples if data_args.max_train_samples is not None else len(train_dataset)
        )
        metrics[TRAIN_SAMPLES] = min(max_train_samples, len(train_dataset))

        # trainer.save_model()  # Saves the tokenizer too for easy upload

        trainer.log_metrics(TRAIN, metrics)
        trainer.save_metrics(TRAIN, metrics)
        trainer.save_state()

    # Evaluation
    if training_args.do_eval:
        logger.info("*** Evaluate ***")

        metrics = trainer.evaluate(eval_dataset=eval_dataset)

        max_eval_samples = (
            data_args.max_eval_samples if data_args.max_eval_samples is not None else len(eval_dataset)
        )
        metrics[EVAL_SAMPLES] = min(max_eval_samples, len(eval_dataset))

        trainer.log_metrics(EVAL, metrics)
        trainer.save_metrics(EVAL, metrics)

    if training_args.do_predict:
        logger.info("*** Predict ***")
        metrics = trainer.predict(predict_dataset=predict_dataset)
        max_predict_samples = (
            data_args.max_predict_samples if data_args.max_predict_samples is not None else len(predict_dataset)
        )
        metrics[PREDICT_SAMPLES] = min(max_predict_samples, len(predict_dataset))
        trainer.log_metrics(PREDICT, metrics)
        trainer.save_metrics(PREDICT, metrics)
    return trainer


def main():
    parser = HfArgumentParser(
        (DataTrainingArguments, ModelArguments, ProjectSeq2SeqTrainingArguments),
        description=DESCRIPTION,
    )
    data_args, model_args, training_args = parser.parse_args_into_dataclasses()

    # Set extra arguments here
    if training_args.run_name == AUTO:
        training_args.run_name = f"epochs={training_args.num_train_epochs}_batch={training_args.per_device_train_batch_size}_lr={training_args.learning_rate}"
    if training_args.output_dir == AUTO:
        training_args.output_dir = EXPERIMENTS_DIR / training_args.run_name

    # Setup logging
    setup_logging(data_args, model_args, training_args, logger)
    if training_args.report_to in [WANDB, ALL]:
        os.environ[WANDB_PROJECT] = PROJECT_NAME

    # Set seed before initializing model.
    set_seed(training_args.seed)

    # Load datasets
    raw_datasets = load_dataset(data_args.dataset)
    raw_datasets = preprocess_datasets(data_args, model_args, training_args, raw_datasets)

    # run training
    trainer = train_model(data_args, model_args, training_args, raw_datasets)


if __name__ == "__main__":
    main()
