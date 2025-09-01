param (
    [switch]$EnableChinaConfig
)

# Define the user directory
$userProfile = [System.Environment]::GetFolderPath("UserProfile")

# Define the path to the .condarc configuration file
$condaPath = Join-Path -Path $userProfile -ChildPath ".conda"

# Check if the .conda directory exists
if (Test-Path $condaPath) {
    Write-Host "Miniconda is already installed."
    # Get the Start Menu shortcut folder path
    $startMenuPath = [System.Environment]::GetFolderPath("StartMenu")  # Get the Start Menu path

    # Define the shortcut name for Anaconda PowerShell Prompt
    $condaShortcutName = "Anaconda PowerShell Prompt"  # Adjust to the correct shortcut name if necessary

    # Search for the conda-related shortcut files
    $condaShortcut = Get-ChildItem -Path $startMenuPath -Recurse -Filter "*$condaShortcutName*.lnk" -ErrorAction SilentlyContinue

    # Check if the shortcut was found
    if ($condaShortcut) {
        # Get the target path of the shortcut and arguments (if any)
        foreach ($shortcut in $condaShortcut) {
            $shortcutObject = (New-Object -ComObject WScript.Shell).CreateShortcut($shortcut.FullName)
            $arguments = $shortcutObject.Arguments  # This retrieves the command line arguments

            # Use a regular expression to extract the conda installation path from the arguments string
            if ($arguments -match "& '([^']+)\\shell\\condabin\\conda-hook.ps1") {
                $condaInstallPath = $matches[1]  # Extract the Conda installation path
                Write-Host "Conda install directory: $condaInstallPath"
            }
            else {
                Write-Host "Conda install directory could not be extracted from arguments."
            }
        }
    }
    else {
        Write-Host "No 'Anaconda PowerShell Prompt' shortcut found in Start Menu."
    }
}
else {
    Write-Host "Miniconda is not installed, downloading Miniconda..."

    # Miniconda download link (Windows 64-bit)
    $minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    $destinationPath = "$userProfile\Downloads\Miniconda3-latest-Windows-x86_64.exe"

    # Download the Miniconda installer
    Invoke-WebRequest -Uri $minicondaUrl -OutFile $destinationPath

    Write-Host "Miniconda download completed, starting silent installation..."

    # Install Miniconda (silent mode)
    Start-Process -FilePath $destinationPath -ArgumentList "/S" -Wait

    Write-Host "Miniconda installation completed."

    # Remove the installer
    Remove-Item $destinationPath -Force

    $condaInstallPath = "$userProfile\miniconda3"
}

# Create a new conda virtual environment
$condaEnvName = "cracknuts"

$condaHookPath = Join-Path -Path $condaInstallPath -ChildPath "shell\condabin\conda-hook.ps1"

. $condaHookPath

# Enable the conda TUAN mirror for faster package downloads in China
if ($EnableChinaConfig) {
    Write-Host "Enable the conda TUAN mirror for faster package downloads in China..."
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    conda config --set show_channel_urls yes
}

# Retrieve the list of all Conda environments
$envList = conda env list | Select-String -Pattern "^\s*$condaEnvName\s+" | ForEach-Object { $_.Line }

# Check if the specified environment exists
if ($envList.Count -gt 0) {
    Write-Host "Conda environment '$condaEnvName' already exists. No need to create."
}
else {
    Write-Host "Conda environment '$condaEnvName' does not exist. Creating the environment..."
    # Create the Conda environment and install Python 3.12
    conda create -n $condaEnvName python=3.12 -y
    Write-Host "Conda environment '$condaEnvName' created successfully."
}

# Activate the conda environment
conda activate $condaEnvName

# Enable pip ALIYUN mirror for faster package downloads in China
if ($EnableChinaConfig) {
    Write-Host "Enable the pip ALIYUN mirror for faster package downloads in China..."
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
    pip config set install.trusted-host mirrors.aliyun.com
}

# Install the required packages
Write-Host "Install or update cracknuts package..."
pip install -U cracknuts[jupyter]

# Download the CrackNuts icon
if ($EnableChinaConfig) {
    $iconUrl = "https://cracknuts.cn/img/logo.ico"
} else {
    $iconUrl = "https://cracknuts.io/img/logo.ico"
}
$userProfile = [System.Environment]::GetFolderPath("UserProfile") # Get the user profile directory
$iconDirPath = Join-Path -Path $userProfile -ChildPath ".cracknuts"
New-Item -Path $iconDirPath -ItemType Directory -Force
$iconPath = Join-Path -Path $iconDirPath -ChildPath "logo.ico"

$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($iconUrl, $iconPath)

# Define the target application path
$targetPath = "%WINDIR%\System32\WindowsPowerShell\v1.0\powershell.exe"
$arguments = "-ExecutionPolicy ByPass -NoExit -Command ""& '$condaInstallPath\shell\condabin\conda-hook.ps1' ; conda activate $condaEnvName ; cracknuts welcome"""
$argumentsLab = "-ExecutionPolicy ByPass -NoExit -Command ""& '$condaInstallPath\shell\condabin\conda-hook.ps1' ; conda activate $condaEnvName ; cracknuts tutorials"""
$shortcutName = "CrackNuts"  # Name of the shortcut
$labShortcutName = "CrackNuts Tutorials"  # Name of the shortcut
$desktopPath = [System.Environment]::GetFolderPath("Desktop")  # Get the Desktop folder path
$startMenuPath = [System.Environment]::GetFolderPath("Programs")  # Get the Start Menu folder path

# Create the WScript.Shell COM object to create shortcuts
$shell = New-Object -ComObject WScript.Shell

# Define the full paths for the shortcut on Desktop and Start Menu
$desktopShortcutPath = Join-Path -Path $desktopPath -ChildPath "$shortcutName.lnk"
$startMenuShortcutPath = Join-Path -Path $startMenuPath -ChildPath "$shortcutName.lnk"
$desktopLabShortcutPath = Join-Path -Path $desktopPath -ChildPath "$labShortcutName.lnk"
$startMenuLabShortcutPath = Join-Path -Path $startMenuPath -ChildPath "$labShortcutName.lnk"

# Create shortcut on Desktop
$desktopShortcut = $shell.CreateShortcut($desktopShortcutPath)
$desktopShortcut.TargetPath = $targetPath
$desktopShortcut.Arguments = $arguments
$desktopShortcut.IconLocation = $iconPath
$desktopShortcut.WorkingDirectory = $userProfile
$desktopShortcut.Save()

# Create shortcut in Start Menu
$startMenuShortcut = $shell.CreateShortcut($startMenuShortcutPath)
$startMenuShortcut.TargetPath = $targetPath
$startMenuShortcut.Arguments = $arguments
$startMenuShortcut.IconLocation = $iconPath
$startMenuShortcut.WorkingDirectory = $userProfile
$startMenuShortcut.Save()

# Create shortcut on Desktop
$desktopLabShortcut = $shell.CreateShortcut($desktopLabShortcutPath)
$desktopLabShortcut.TargetPath = $targetPath
$desktopLabShortcut.Arguments = $argumentsLab
$desktopLabShortcut.IconLocation = $iconPath
$desktopLabShortcut.WorkingDirectory = $userProfile
$desktopLabShortcut.Save()

# Create shortcut in Start Menu
$startMenuLabShortcut = $shell.CreateShortcut($startMenuLabShortcutPath)
$startMenuLabShortcut.TargetPath = $targetPath
$startMenuLabShortcut.Arguments = $argumentsLab
$startMenuLabShortcut.IconLocation = $iconPath
$startMenuLabShortcut.WorkingDirectory = $userProfile
$startMenuLabShortcut.Save()

Write-Host "Shortcut created on Desktop and Start Menu."
Write-Host "Installation successful."

