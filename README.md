# Setup

```bash
python3 -m venv venv # create a venv

# activate the venv
# use only one command here depending on your shell:
.\venv\Scripts\activate.bat # Windows cmd.exe
.\venv\Scripts\Activate.ps1 # Windows powershell
source venv/bin/activate # POSIX bash
source venv/bin/activate.zsh # POSIX zsh

pip install -r requirements.txt # install dependencies to venv

python3 main.py # run program
```