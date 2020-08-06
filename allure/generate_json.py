import json

from allure.json_reporter import JSONReporter

PATHS_LIST_FILE_PATH = 'paths.txt'
OUTPUT_RESULTS_FILE = 'results.json'
config = None


def read_config():
    with open('config.json', 'r') as json_file:
        return json.load(json_file)


def get_input_paths():
    with open(PATHS_LIST_FILE_PATH, 'r') as f:
        return [line.strip() for line in f.readlines() if not line.startswith("#")]


def main():
    JSONReporter(get_input_paths(), OUTPUT_RESULTS_FILE, read_config()).report()


if __name__ == "__main__":
    main()
