# Link Clicker

## Setup: `Installation`

### Create virtual environments by executing the following command:

```bash
sudo -s
```
```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

### Run this command to install dependencies:
```bash
pip install -r requirements.txt
```
---
### To install windscribe-cli just simply follow this instruction:

**Step 1:** Open your Terminal and add the windscribe signing key to apt using following command.
```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key FDC247B7
```

**Step 2:** Add the repository to your source.list using the following command
```bash
echo 'deb https://repo.windscribe.com/ubuntu bionic main' | sudo tee /etc/apt/sources.list.d/windscribe-repo.list
```
**Step 3:** Update package list
```bash
sudo apt-get update
```
**Step 4:** Install windscribe-cli use the following command.
```bash
sudo apt-get install windscribe-cli
```
---
### To install Google Chrome from the terminal

**Step 1:** Get the DEB file using the wget command:
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
```
**Step 2:** 

Use dpkg to install Chrome from the downloaded DEB file
```bash
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

**Step 3:** Update package list
```bash
sudo apt-get update
```
---
**Run this command:**
```bash
python index.py
```

