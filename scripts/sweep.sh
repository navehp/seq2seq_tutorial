PROJECT_NAME=seq2seq_tutorial
SWEEP_CONFIG=sweep.yaml
wandb sweep ${SWEEP_CONFIG} --project ${PROJECT_NAME}
echo "Copy the sweep ID to the agents.sh file!"