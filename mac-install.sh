#!/usr/bin/env bash
echo "This script will install all necessary Mac dependencies as well as Homebrew if it is not already installed."
if test ! $(which brew); then
    echo "Installing homebrew..."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

# Update homebrew recipes
brew update
brew install gtk+3
brew install pygobject3
