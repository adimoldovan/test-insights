import datetime
import json
import os
from decimal import Decimal
from operator import itemgetter
from os import listdir
from os.path import isfile, join
from pathlib import Path
from shutil import copyfile

import boto3

from py.result import Result


class JSONReporterAllure:
    def __init__(self, paths_list, output_results_file, config):
        self.paths_list = paths_list
        self.output_results_file = output_results_file
        self.config = config
        self.results = {"meta": {}, "tests": {}}
        self.existing_uuids = []
        self.processed_files = 0
        self.skipped_results = 0
        self.added_results = 0

    def report(self):
        # backup existing report
        f = Path(self.output_results_file)

        if f.exists():
            bkf_name = os.path.splitext(f.name)[0]
            bkf = os.path.join(
                f.parent, "{}-{}.json".format(bkf_name, datetime.datetime.now())
            )
            copyfile(f, bkf)
            print("Created backup report: {}".format(bkf))

        # Create output dir if report doesn't exist yet
        Path(f.parent).mkdir(parents=True, exist_ok=True)

        self.get_existing_results()
        for path in self.paths_list:
            self.add_results_from_path(path)
        # run it twice because if the first found result is passed
        # and doesn't already exists it will be ignored
        for path in self.paths_list:
            self.add_results_from_path(path)

        self.create_insights()
        self.create_aggregated_json()

    def add_results_from_s3(self, s3_path):
        s3 = boto3.resource("s3")
        s3_path = s3_path.replace("s3://", "")
        segments = s3_path.split("/")
        bucket_name = segments[0]
        segments.pop(0)
        prefix = "/".join(segments)
        bucket = s3.Bucket(bucket_name)

        for obj in bucket.objects.filter(Prefix=prefix):
            if obj.key.endswith("-result.json"):
                # print(obj.key)
                self.add_result(obj.get()["Body"])

    def add_results_from_path(self, results_path):
        print()
        print(results_path)
        print(
            "-------------------------------------------------------------------------------------------------------"
        )
        print(
            "{:<50s}{:<15s}{:<15s}{:<15s}".format(
                "", "Processed", "Added", "Skipped/Ignored"
            )
        )
        print(
            "-------------------------------------------------------------------------------------------------------"
        )
        if results_path.startswith("s3://"):
            self.add_results_from_s3(results_path)
        else:
            for file in [
                f for f in listdir(results_path) if isfile(join(results_path, f))
            ]:
                if file.endswith("-result.json"):
                    with open(join(results_path, file), "r") as content:
                        self.add_result(content)
        print()
        print(
            "-------------------------------------------------------------------------------------------------------"
        )

    def add_result(self, result_content):
        json_data = json.load(result_content)
        action = ""
        self.processed_files += 1

        if self.is_ignored(json_data["fullName"]):
            # print("Ignoring {}".format(json_data['fullName']))
            action = "ignored"
            self.skipped_results += 1
            return

        if json_data["uuid"] in self.existing_uuids:
            # print("Result {0} already exists".format(json_data['uuid']))
            action = "already exists"
            self.skipped_results += 1
            return

        if (
            json_data["status"] in ["broken", "failed"]
            or json_data["fullName"] in self.results["tests"]
        ):
            result = Result(
                json_data["status"],
                json_data["uuid"],
                json_data["start"],
                json_data["stop"],
                json_data["statusDetails"].get("trace"),
            )

            if json_data["fullName"] not in self.results["tests"]:
                self.results["tests"][json_data["fullName"]] = {"results": []}

            # print("Adding {0} result {1}".format(result.status, result.uuid))
            self.results["tests"][json_data["fullName"]]["results"].append(
                result.__dict__
            )
            self.results["tests"][json_data["fullName"]]["results"].sort(
                key=itemgetter("stop")
            )
            self.existing_uuids.append(result.uuid)
            action = "added"
            self.added_results += 1
        else:
            action = "skipped"
            self.skipped_results += 1

        print(
            "{:<50s}{:<15n}{:<15n}{:<15n}".format(
                "{0}-{1}".format(json_data["uuid"], action),
                self.processed_files,
                self.added_results,
                self.skipped_results,
            ),
            end="\r",
        )

    def is_ignored(self, full_name):
        for partial_name in self.config.get("ignore"):
            return partial_name in full_name

    def create_insights(self):
        # insights per test case
        for test in self.results["tests"]:
            res = self.results["tests"][test]["results"]
            status_list = [r["status"].lower() for r in res]
            failures = status_list.count("failed") + status_list.count("broken")
            solved = status_list.count("solved")
            self.results["tests"][test]["failure_rate"] = int(
                Decimal(failures / status_list.__len__()) * 100
            )
            self.results["tests"][test]["runs"] = len(
                self.results["tests"][test]["results"]
            )
            self.results["tests"][test]["failures"] = failures
            self.results["tests"][test]["solved"] = solved

        # totals
        self.results["meta"]["affected_test_cases"] = len(self.results["tests"])
        self.results["meta"]["failed_test_cases"] = sum(
            1
            for tc in self.results["tests"]
            if self.results["tests"][tc]["failure_rate"] > 0
        )
        self.results["meta"]["solved_test_cases"] = (
            self.results["meta"]["affected_test_cases"]
            - self.results["meta"]["failed_test_cases"]
        )
        self.results["meta"]["total_runs"] = sum(
            self.results["tests"][tc]["runs"] for tc in self.results["tests"]
        )
        self.results["meta"]["total_failed_runs"] = sum(
            self.results["tests"][tc]["failures"] for tc in self.results["tests"]
        )
        self.results["meta"]["failure_rate"] = int(
            Decimal(
                self.results["meta"]["total_failed_runs"]
                / self.results["meta"]["total_runs"]
            )
            * 100
        )
        self.results["meta"]["solved_results"] = sum(
            self.results["tests"][tc]["solved"] for tc in self.results["tests"]
        )

    def create_aggregated_json(self):
        with open(self.output_results_file, "w") as file:
            json.dump(self.results, file, indent=2, sort_keys=True)
        print()
        print("Results saved in {0}".format(self.output_results_file))

    def get_existing_results(self):
        if Path(self.output_results_file).is_file():
            with open(self.output_results_file, "r") as json_file:
                self.results = json.load(json_file)

        for test in self.results["tests"]:
            for result in self.results["tests"][test]["results"]:
                self.existing_uuids.append(result["uuid"])
