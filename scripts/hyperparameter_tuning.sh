DATASET="xsum"
MODEL_NAME_OR_PATH="t5-small"
MAX_TRAIN_SAMPLES=5000
MAX_EVAL_SAMPLES=1000
RUN_NAME="auto"
OUTPUT_DIR="auto"
NUM_TRAIN_EPOCHS=15
PER_DEVICE_TRAIN_BATCH_SIZE=1
PER_DEVICE_EVAL_BATCH_SIZE=1
EVALUATION_STRATEGY="epoch"
METRIC_FOR_BEST_MODEL="eval/bertscore_f1"
SAVE_STRATEGY="epoch"
SAVE_TOTAL_LIMIT=1
SEED=0
REPORT_TO="wandb"

for LEARNING_RATE in 0.000001 0.00005 0.0001 0.0005 0.001
  do
    for GRADIENT_ACCUMULATION_STEPS in 1 2 4 8 16
    do
      python main_seq2seq.py \
        --dataset ${DATASET} \
        --model_name_or_path ${MODEL_NAME_OR_PATH} \
        --output_dir ${OUTPUT_DIR} \
        --do_train \
        --do_eval \
        --max_train_samples ${MAX_TRAIN_SAMPLES} \
        --max_eval_samples ${MAX_EVAL_SAMPLES} \
        --num_train_epochs ${NUM_TRAIN_EPOCHS} \
        --per_device_train_batch_size ${PER_DEVICE_TRAIN_BATCH_SIZE} \
        --per_device_eval_batch_size ${PER_DEVICE_EVAL_BATCH_SIZE} \
        --evaluation_strategy ${EVALUATION_STRATEGY} \
        --load_best_model_at_end \
        --metric_for_best_model ${METRIC_FOR_BEST_MODEL} \
        --save_strategy ${SAVE_STRATEGY} \
        --save_total_limit ${SAVE_TOTAL_LIMIT} \
        --seed ${SEED} \
        --report_to ${REPORT_TO} \
        --learning_rate ${LEARNING_RATE} \
        --gradient_accumulation_steps ${GRADIENT_ACCUMULATION_STEPS} \
        --run_name ${RUN_NAME}
  done
done