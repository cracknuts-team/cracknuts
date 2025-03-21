#!/bin/bash

# Enable China configuration if needed
ENABLE_CHINA_CONFIG=false
while [[ "$1" != "" ]]; do
  case $1 in
    --china-config ) ENABLE_CHINA_CONFIG=true
      ;;
  esac
  shift
done

# Define user home directory
USER_HOME="$HOME"

# Check if Conda is installed
if command -v conda &> /dev/null; then
    echo "Conda is already installed."
    CONDA_INSTALL_PATH="$(conda info --base)"
else
    echo "Miniconda is not installed, downloading Miniconda..."
    
    # Miniconda download link (Linux 64-bit)
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    DESTINATION_PATH="$USER_HOME/Downloads/Miniconda3-latest-Linux-x86_64.sh"
    
    # Download the Miniconda installer
    curl -L "$MINICONDA_URL" -o "$DESTINATION_PATH"
    
    echo "Miniconda download completed, starting silent installation..."
    
    # Install Miniconda (silent mode)
    bash "$DESTINATION_PATH" -b -p "$USER_HOME/miniconda3"
    rm "$DESTINATION_PATH"
    
    echo "Miniconda installation completed."
    CONDA_INSTALL_PATH="$USER_HOME/miniconda3"
fi

# Initialize conda
source "$CONDA_INSTALL_PATH/etc/profile.d/conda.sh"

# Create a new conda virtual environment
CONDA_ENV_NAME="cracknuts"
if conda env list | grep -q "^$CONDA_ENV_NAME "; then
    echo "Conda environment '$CONDA_ENV_NAME' already exists. No need to create."
else
    echo "Creating Conda environment '$CONDA_ENV_NAME'..."
    conda create -n "$CONDA_ENV_NAME" python=3.12 -y
    echo "Conda environment '$CONDA_ENV_NAME' created successfully."
fi

# Activate the conda environment
conda activate "$CONDA_ENV_NAME"

conda init

# Enable TUNA mirror for faster package downloads in China
if [ "$ENABLE_CHINA_CONFIG" = true ]; then
    echo "Enabling conda TUNA mirror..."
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    conda config --set show_channel_urls yes
fi

# Enable pip ALIYUN mirror for faster package downloads in China
if [ "$ENABLE_CHINA_CONFIG" = true ]; then
    echo "Enabling pip ALIYUN mirror..."
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
    pip config set install.trusted-host mirrors.aliyun.com
fi

# Install the required packages
echo "Installing or updating cracknuts package..."
pip install -U "cracknuts[jupyter]"

# Download CrackNuts icon
if [ "$ENABLE_CHINA_CONFIG" = true ]; then
    ICON_URL="https://cracknuts.cn/img/icon.svg"
else
    ICON_URL="https://cracknuts.io/img/icon.svg"
fi
ICON_DIR_PATH="$USER_HOME/.cracknuts"
mkdir -p "$ICON_DIR_PATH"
ICON_PATH="$ICON_DIR_PATH/icon.svg"
curl -L "$ICON_URL" -o "$ICON_PATH"

# Creat cracknuts bashrc.sh
CRACKNUTS_BASHRC_PATH="$USER_HOME/.cracknuts/bashrc.sh"
cat << EOF > "$CRACKNUTS_BASHRC_PATH"
source ~/.bashrc
source $CONDA_INSTALL_PATH/etc/profile.d/conda.sh
conda activate cracknuts
cracknuts welcome
cd $USER_HOME
EOF

# Create cracknuts tutorials bashrc.sh
CRACKNUTS_TUTORIALS_BASHRC_PATH="$USER_HOME/.cracknuts/tutorials_bashrc.sh"
cat << EOF > "$CRACKNUTS_TUTORIALS_BASHRC_PATH"
source ~/.bashrc
source $CONDA_INSTALL_PATH/etc/profile.d/conda.sh
conda activate cracknuts
cracknuts tutorials
EOF

SHORTCUT_BASE_PATH="$HOME/.local/share/applications"
mkdir -p "$SHORTCUT_BASE_PATH"

# Create Cracknuts shortcut
SHORTCUT_PATH="$SHORTCUT_BASE_PATH/cracknuts.desktop"
cat << EOF > "$SHORTCUT_PATH"
[Desktop Entry]
Version=1.0
Type=Application
Name=CrackNuts
Exec=bash --rcfile "$CRACKNUTS_BASHRC_PATH"
Icon=$ICON_PATH
Terminal=true
Categories=Science
EOF

# Create Tutorials shortcut
TUTORIALS_SHORTCUT_PATH="$SHORTCUT_BASE_PATH/cracknuts_tutorials.desktop"
cat << EOF > "$TUTORIALS_SHORTCUT_PATH"
[Desktop Entry]
Version=1.0
Type=Application
Name=CrackNuts Tutorials
Exec=bash --rcfile "$CRACKNUTS_TUTORIALS_BASHRC_PATH"
Icon=$ICON_PATH
Terminal=true
Categories=Science
EOF

echo "Shortcuts created successful."
echo "Installation successful."
