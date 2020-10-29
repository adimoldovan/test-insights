import json
import os
import re


class Processor:
    def __init__(self, config):
        self.config = config
        self.json_report = os.path.join(
            config["output"]["dir"], config["output"]["json"]
        )
        self.results = None

    def read_file(self):
        with open(self.json_report, "r") as json_file:
            self.results = json.load(json_file)

    def write_file(self):
        with open(self.json_report, "w") as file:
            json.dump(self.results, file, indent=2, sort_keys=True)

    def report(self, ):
        if self.config["short_stacktrace"]:
            self.reduce_stack_traces()

        self.write_file()

    def reduce_stack_traces(self):
        self.read_file()

        for test in self.results["tests"]:
            for result in self.results["tests"][test]["results"]:
                if result["trace"] is not None:
                    result["trace"] = re.sub("\tat.*\n", "", result["trace"])
