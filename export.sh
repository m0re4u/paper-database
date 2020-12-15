#!/bin/bash

METHOD=pandoc

echo -e "\033[0;32mRunning export in $METHOD...\033[0m"
if [ $METHOD == jabref ]; then
  jabref --import papers.bib --output exported/papers.md,simple_with_link --nogui
elif [ $METHOD == pandoc ]; then
  pandoc -o output.md papers.bib
fi

echo -e "\033[0;32mDeploying updates to GitHub...\033[0m"

git add .

# Commit changes.
msg="Exporting paper database at `date`"
if [ $# -eq 1 ]
  then msg="$1"
fi
git commit -m "$msg"

git push origin master

