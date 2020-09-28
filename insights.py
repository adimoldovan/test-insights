import argparse
import json

from py.html_reporter import HTMLReporter
from py.json_reporter import JSONReporterAllure


def generate_insights():
    print()
    print("=========================================================")
    print("Generating results json file")
    print("=========================================================")
    print()

    # Get config from file
    conf = read_config()

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", help="output directory path")
    parser.add_argument("--output_json", help="output json report file name")
    parser.add_argument("--output_html", help="output html report file name")
    parser.add_argument("--paths_file", help="path to file containing the source paths")
    # parser.add_argument("--source", help="source type (Allure, Junit)")

    args = parser.parse_args()

    if args.output_dir:
        print("Will write output to %s" % args.output_dir)
        conf["output"]["dir"] = args.output_dir

    if args.output_json:
        print("Will save the JSON report as %s" % args.output_json)
        conf["output"]["json"] = args.output_json

    if args.output_html:
        print("Will save the HTML report as %s" % args.output_html)
        conf["output"]["html"] = args.output_html

    if args.paths_file:
        print("Will read results paths from %s" % args.paths_file)
        conf["input"] = args.paths_file

    # If the source is Allure results
    JSONReporterAllure(conf).report()

    print()
    print("=========================================================")
    print("Generating HTML report")
    print("=========================================================")
    print()

    HTMLReporter(conf).report()

    print("=========================================================")


def read_config():
    with open("config/config.json", "r") as config_file:
        return json.load(config_file)


if __name__ == "__main__":
    generate_insights()
