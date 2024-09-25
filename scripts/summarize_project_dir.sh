#!/bin/bash

# Check if the project directory is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <project_directory>"
  exit 1
fi

# Define the project directory
project_dir="$1"
project_name=$(basename "$project_dir")

# Define the directories to summarize
dirs=("src" "docs")

# Create the markdown summary file in the root of the project directory
summary_file="$project_dir/${project_name}_summary.md"
> "$summary_file"

# Write the title to the markdown file
echo "# Summary of $project_name" >> "$summary_file"
echo "" >> "$summary_file"

# Function to summarize a directory
summarize_dir() {
  local dir="$1"
  echo "## Directory: $dir" >> "$summary_file"
  echo "" >> "$summary_file"
  
  # Iterate over the files in the directory
  find "$dir" -type f | while read -r file; do
    echo "### File: $file" >> "$summary_file"
    echo "" >> "$summary_file"
    echo '```bash' >> "$summary_file"
    head -n 15 "$file" >> "$summary_file"
    echo '```' >> "$summary_file"
    echo "" >> "$summary_file"
  done
  
  echo "" >> "$summary_file"
}

# Summarize each directory
for dir in "${dirs[@]}"; do
  if [ -d "$project_dir/$dir" ]; then
    summarize_dir "$project_dir/$dir"
  else
    echo "## Directory $project_dir/$dir does not exist." >> "$summary_file"
  fi
done

echo "Summary written to $summary_file"
