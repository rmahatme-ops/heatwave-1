# Heatwave Watch — Streamlit

This project uses the supplied climate dataset (`heatwave_data.csv`) and is configured for Streamlit Community Cloud.

## Included files
- `app.py` — Streamlit dashboard and filters.
- `heatwave_data.csv` — your supplied dataset, copied into this project.
- `requirements.txt` — required Python packages.
- `README.md` — setup and deployment guide.
- `region_bst.c` — companion C binary-search-tree range-query example; it is not called by the Streamlit app.
- `.gitignore` — ignores virtual environments and local secrets.

## Dataset columns
The supplied dataset contains `region`, `city`, `lat`, `lon`, `Date`, `Rain`, `Temp Max`, and `Temp Min`. The app automatically maps `Date` to `date`, `Temp Max` to `tmax`, and `Temp Min` to `tmin`. Dates are parsed in day-month-year order, matching values like `01-01-1951`.

## Run locally on Windows
1. Extract the ZIP and open the extracted folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal and activate again.
5. Install packages:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. Run:
   ```powershell
   streamlit run app.py
   ```
7. Open the local URL printed in the terminal, usually `http://localhost:8501`.

Stop the app with `Ctrl+C`.

## Deploy to Streamlit Community Cloud
1. Sign in to GitHub and create a repository.
2. Upload `app.py`, `requirements.txt`, and `heatwave_data.csv` to the repository root. Keep the app and requirements file at the top level.
3. Visit https://share.streamlit.io/ and sign in with GitHub.
4. Create/deploy an app, choose your repository and branch, and set the main file path to `app.py`.
5. Click **Deploy** and wait for the build to finish.

### Dataset size note
The provided CSV is about 18 MB. It is included in this project ZIP. GitHub generally accepts this file size, but uploading the CSV through a browser can be slow. If the dataset is private or restricted, do not put it in a public repository. Consider private repository access or a suitable private data source.

## Troubleshooting
- `FileNotFoundError`: make sure `heatwave_data.csv` is next to `app.py`.
- `ModuleNotFoundError`: activate `.venv`, then run `pip install -r requirements.txt`.
- `streamlit` not recognized: use `python -m streamlit run app.py`.
- Missing-column error: expected `region`, `lat`, `lon`, and `Date`/`date`, `Temp Max`/`tmax`.
- No results: select a region and date range that contain observations.

## C file
`region_bst.c` is included as a companion algorithm demonstration. The dashboard currently filters with Pandas and does not compile or call the C code.
