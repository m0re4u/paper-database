#!/bin/bash

METHOD=python

echo -e "\033[0;32mRunning export in $METHOD...\033[0m"
if [ $METHOD == jabref ]; then
  jabref --import papers.bib --output exported/papers.md,simple_with_link --nogui
elif [ $METHOD == python ]; then
  python3 export.py papers.bib
fi

