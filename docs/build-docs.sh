#!/bin/bash

LOCALTEX=$(cat spec.tex);
WEBTEX=$(curl -L "https://phseiff.com/gender-render/spec.tex");

LATEXVERSION=$(tr "\n" "|" < "spec.tex" | tr "{" "_" | tr "}" "_" | xargs | grep -Po "version__\K(.*?)_");
ONLINELATEXVERSION=$(curl -L "https://phseiff.com/gender-render/spec.version.txt");

if [ "$LATEXVERSION" == "$ONLINELATEXVERSION" ]
then
  echo "Didn't change:";
  echo "local version:";
  echo "$LATEXVERSION";
  echo "web version:";
  echo "$ONLINELATEXVERSION";
else
  # Update packages:
  sudo apt-get update --fix-missing;

  # Create new version of specification:
  sudo apt-get install xzdec;
  sudo apt-get install texlive-latex-base;
  mkdir ~/texmf;
  tlmgr init-usertree;
  sudo tlmgr option repository ftp://tug.org/historic/systems/texlive/2017/tlnet-final;
  tlmgr install caption;

  # Convert specifications:
  python3 texliveonthefly.py spec.tex;
fi