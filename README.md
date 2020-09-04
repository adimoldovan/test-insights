# test-insights

Generates a single HTML report with an overview of the test results.
Source can be:
- multiple Allure json results
- multiple JUnit result files (to be implemented)

## Setup and usage

### Setup
- install Python 3.8
- create a virtual environment `python3 -m venv venv`
- activate the virtual environment `. venv/bin/activate`
- install dependencies `pip install -r requirements.txt`

### Configure
- you can update the script configuration by updating `config/config.json` 
- add the source paths in `config/paths.txt`. They can be local paths or S3 buckets paths.

### Run
- run the script: `pyton3 insights.py`
