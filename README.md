# WiFiToggle Utility

WiFiToggle is a utility that toggles your Wi-Fi adapter between 5 GHz and 2.4 GHz modes. It does so by modifying the relevant registry settings for your Wi-Fi adapter and then restarting the adapter for the changes to take effect. This README guides you through the setup, installer build process, and how to correctly identify the registry details needed by the utility.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Finding Your Adapter Registry Key and Values](#finding-your-adapter-registry-key-and-values)
- [Building the Installer](#building-the-installer)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Prerequisites

- **Operating System:** Windows 10 or 11
- **Python:** Version 3.6 or higher (if running from source)
- **Administrator Privileges:** Needed to modify registry settings and restart the network adapter.
- **Required Python Packages:** Listed in [requirements.txt](requirements.txt). These include:
    - `pystray` (for tray icon support)
    - `Pillow` (required by pystray for image handling)
    - `elevate` (to run the program with elevated privileges)
    - *PyInstaller* (used during installer build, recommended to be installed separately)

---

## Installation

1. **Clone or Download the Repository:**
    - Download the project files to your local machine.

2. **Set Up a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
    - Install the required packages using:
      ```bash
      pip install -r requirements.txt
      ```

---

## Finding Your Adapter Registry Key and Values

This utility uses registry settings to toggle the Wi-Fi band modes. Follow these steps to accurately obtain the necessary details:

1. **Identify Your Wi-Fi Adapter:**
    - Open **Device Manager**:
        - Right-click on the Start button and select **Device Manager**.
    - Expand the **Network adapters** category.
    - Locate your Wi-Fi adapter (commonly identifiable by its name and manufacturer).
    - Right-click the adapter and select **Properties**.
    - Under the **Advanced** tab, review settings like "Wireless Mode" or "Preferred Band". These options show how the adapter is configured to handle different bands.

2. **Determine the Registry Key Path:**
    - Press **Windows + R**, type `regedit`, and press **Enter** to launch the Registry Editor.
    - Navigate to the following base path:
      ```
      HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}
      ```
    - Under this key, multiple subkeys (e.g., `0000`, `0001`, etc.) exist. Click each one and look for entries that match your Wi-Fi adapter's details (you might find the adapter's name or related descriptions).
    - Once you find the correct subkey, note the full registry key path. This value should be used as the adapter key path in the utility.

3. **Identify the Values for 5 GHz and 2.4 GHz Modes:**
    - In the correct registry subkey, find the value (or values) that corresponds to wireless mode settings.
    - Compare these settings with the options under the **Advanced** tab in Device Manager to confirm which registry value controls the 5 GHz and which controls the 2.4 GHz output.
    - Record:
        - **VALUE_5GHZ:** The registry value that enables or indicates 5 GHz mode.
        - **VALUE_24GHZ:** The registry value that enables or indicates 2.4 GHz mode.
    - These recorded values are used by the utility when toggling the Wi-Fi band.

---

## Building the Installer

For ease of distribution, you can build a standalone executable using PyInstaller. A batch file is provided to simplify the process.

1. **Run the Installer Build Script:**
    - Open a command prompt in the project directory.
    - Execute the following command:
      ```plain text
      generate_installer.bat
      ```
    - The batch script uses PyInstaller with these options:
        - `--onefile`: Bundles everything into a single executable.
        - `--noconsole`: Hides the console window (useful for reducing distractions if using tray icons).
        - `--uac-admin`: Ensures the application prompts for administrator privileges.
        - `--name WiFiToggle`: Sets the name of the executable.

2. **Locate the Executable:**
    - After the build completes, find `WiFiToggle.exe` in the `dist` folder.

---

## Usage

1. **Run as Administrator:**
    - Ensure that the application runs with administrative privileges, as registry modifications and adapter restarts require elevated rights.

2. **Toggling the Wi-Fi Band:**
    - When executed, the utility will:
        - Read the current mode from the registry.
        - Write the alternate mode value (switching from 5 GHz to 2.4 GHz or vice versa).
        - Restart the Wi-Fi adapter to apply the changes.

3. **Scheduled Task Configuration:**
    - If desired, the utility supports scheduling toggling operations through Windows Scheduled Tasks. Use the provided menu options to install, uninstall, or toggle the task.

---

## Troubleshooting

- **Incorrect Registry Settings:**
    - Revisit the Device Manager and Registry Editor steps to ensure that the correct adapter key path and mode values are in use.

- **Insufficient Privileges:**
    - Make sure the application is run with administrative permissions; otherwise, registry modifications may fail.

- **Adapter Restart Issues:**
    - If the adapter does not restart properly, try manually disabling and then re-enabling it in Device Manager.

- **Logging and Errors:**
    - Check any console or log output provided by the utility for error messages or debugging information.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

If you have any questions or need assistance, please feel free to reach out. Enjoy toggling your Wi-Fi bands easily and efficiently!