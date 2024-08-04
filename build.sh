#!/bin/bash

# Install Rust and Cargo
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Ensure Python and pip are installed
python3 -m ensurepip
python3 -m pip install --upgrade pip

# Install Python packages
python3 -m pip install -r requirements.txt

