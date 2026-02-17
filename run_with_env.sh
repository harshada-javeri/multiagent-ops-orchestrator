#!/bin/bash
# Load environment variables from .env and run prediction

# Load .env file
export $(grep -v '^#' .env | xargs)

# Run prediction
python predict.py "$@"