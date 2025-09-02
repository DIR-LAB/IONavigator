This is the web site code

## Installation instructions

1) Install dependencies:
Make sure you installed ION and ION_Extractor libs
```bash
cd IONavigator/ION
pip install -e .
cd IONavigator/ION_Extractor
pip install -e .
```

2) Set API keys
```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_S3_BUCKET="..."
export MONGODB_CONNECTION_STRING="..."
Make sure you have AWS and MongoDB configured.
```

3) Install Darshan-utils locally
```bash
tar -xvzf darshan-<version-number>.tar.gz
cd darshan-<version-number>/
./prepare.sh
cd darshan-util/
./configure
make
make install
```

## Usage instructions

1) Download preprocessed trace example from [drive folder](https://drive.google.com/drive/folders/1IDKOdpIy5bVT5p2KOWz-XtC_hBmLh8AB?usp=sharing).

2) use `run.py` in `IONavigator/ION` as an example script to get started:
    ```bash
    python3 run.py --trace_path [path_to_downloaded_folder]
    ```
    - By default, all logs will show in the terminal. they can be written to files instead by setting the `ION_LOG_DIR` environment variable to some path.

3) Once the analysis completes, all of the output files of the process are found in the `ION_Output` directory which is automatically created in your current directory. The final diagnosis output can be most easily viewed by opening `ION_Output/final_diagnosis.html` in a browser (i.e. Chrome)


