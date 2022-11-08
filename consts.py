from pathlib import Path

PROJECT_NAME = "seq2seq_tutorial"
DESCRIPTION = """
Learning how to train a Seq2Seq model using the 🤗 Transformers library.
"""

PROJECT_DIR = Path.home() / PROJECT_NAME
DATA_DIR = PROJECT_DIR / "data"
EXPERIMENTS_DIR = PROJECT_DIR / "experiments"

# SCRIPT PATHS
MAIN_PATH = PROJECT_DIR / "main_seq2seq.py"

# GENERAL
AUTO = "auto"
XSUM = "xsum"

# WANDB
WANDB = "wandb"
WANDB_PROJECT = "WANDB_PROJECT"

# SUFFIXES
CSV = '.csv'
JSON = '.json'
TXT = '.txt'
JPG = '.jpg'
PNG = '.png'

# SPLITS
TRAIN = "train"
VALIDATION = "validation"
TEST = "test"
UNLABELED = "unlabeled"
ALL = "all"
SPLITS = [TRAIN, VALIDATION, TEST, UNLABELED]

# PADDING
MAX_LENGTH = "max_length"

# METRICS
ACCURACY = "accuracy"
F1 = "f1"
BERTSCORE_MODEL_NAME = "microsoft/deberta-base-mnli"

# FEATURES
TEXT = "text"
LABELS = "labels"
INPUT_IDS = "input_ids"