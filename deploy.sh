#!/bin/bash

echo -e "\033[0;32mDeploying updates to GitHub...\033[0m"

git add .

# Commit changes.
msg="Updating paper database at `date`"
if [ $# -eq 1 ]
  then msg="$1"
fi

git commit -m "$msg"

git push origin master

