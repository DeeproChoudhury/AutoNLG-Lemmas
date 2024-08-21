python script.py \
    --model mistral-large \
    --input_directory data/full_data/valid/ \
    --messages_directory valid_messages/ \
    --output_directory valid_responses/ \
    --temperature 0.0 \
    --request_timeout 120 \
    --type mistral \
    --num_runs 100