python script.py \
    --model mistral-large \
    --input_directory data/full_data/test/ \
    --messages_directory test_messages/ \
    --output_directory test_responses/ \
    --temperature 0.0 \
    --request_timeout 120 \
    --type mistral \
    --num_runs 100