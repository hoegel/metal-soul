## How to Run (For Users)
1. **Download the latest release** (or build from source).
2. Place the executable (`metal-soul.exe` or `metal-soul`) in the same folder as the `resources` directory.
3. Run the executable.

## For Developers
### Prerequisites
- Python 3.8+
- Pip

### Setup
1. Clone the repository:
    git clone https://github.com/hoegel/metal-soul.git
    cd metal-soul
2. Install dependencies:
    pip install -r requirements.txt
3. Run the app:
    python main.py
### Building the Executable (with PyInstaller)
1. Install PyInstaller:
    pip install pyinstaller(if not in requirements.txt)
2. Build (no --add-data, `resources` must be placed manually next to the executable):
    pyinstaller --noconfirm --windowed --onefile main.py
3. The executable will be in dist/.
    Important: Place the `resources` folder next to the executable for it to work.
### Note on Assets
The app expects the `resources` folder to be in the same directory as the executable.
Do not embed assets using PyInstaller's --add-data—just distribute them alongside the .exe