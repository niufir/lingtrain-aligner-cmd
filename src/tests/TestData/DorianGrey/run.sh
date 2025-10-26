#!/bin/bash

cd "$(dirname "$0")"

conda activate aligner_cmd

export PYTHONIOENCODING=utf-8

# List available files for debugging
echo "Files in current directory:"
ls -la *.epub 2>/dev/null || echo "No EPUB files found"

# Update these filenames to match your actual files
SOURCE_FILE="The Picture of Dorian Gray - Oscar Wilde_en.epub"
TARGET_FILE="Уайлд Оскар. Портрет Дориана Грея (сборник) - royallib.com.epub"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file '$SOURCE_FILE' not found in current directory"
    exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: Target file '$TARGET_FILE' not found in current directory"
    exit 1
fi

python ../../../AlignerCmd.py --pathBookFrom="$SOURCE_FILE" --pathBookTo="$TARGET_FILE" --pathBookOut="en-ru.epub"