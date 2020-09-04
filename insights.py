import json

from html_reporter import HTMLReporter
from json_reporter import JSONReporterAllure


def generate_insights():
    print()
    print("=========================================================")
    print("Generating results json file")
    print("=========================================================")
    print()

    # Get config from file
    conf = read_config()

    with open(conf["input"], "r") as f:
        paths = [line.strip() for line in f.readlines() if not line.startswith("#")]

    # If the source is Allure results
    # JSONReporterAllure(paths, conf["output"]["json"], conf).report()

    print()
    print("=========================================================")
    print("Generating HTML report")
    print("=========================================================")
    print()

    HTMLReporter(conf["output"]["json"], "resources", conf["output"]["html"]).report()

    print("=========================================================")


def read_config():
    with open("config/config.json", "r") as config_file:
        return json.load(config_file)


if __name__ == "__main__":
    generate_insights()
