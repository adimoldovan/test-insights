import json
from decimal import Decimal
from operator import itemgetter
from os import listdir
from os.path import isfile, join
from pathlib import Path

import boto3

from py.result import Result


class JSONReporterAllure:
    def __init__(self, paths_list, output_results_file, config):
        self.paths_list = paths_list
        self.output_results_file = output_results_file
        self.config = config
        self.results = {}
        self.existing_uuids = []
        self.processed_files = 0
        self.skipped_results = 0
        self.added_results = 0

    def report(self):
        # Create output dir
        Path(Path(self.output_results_file).parent).mkdir(parents=True, exist_ok=True)

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
                or json_data["fullName"] in self.results
        ):
            result = Result(
                json_data["status"],
                json_data["uuid"],
                json_data["start"],
                json_data["stop"],
                json_data["statusDetails"].get("trace"),
            )

            if json_data["fullName"] not in self.results:
                self.results[json_data["fullName"]] = {"results": []}

            # print("Adding {0} result {1}".format(result.status, result.uuid))
            self.results[json_data["fullName"]]["results"].append(result.__dict__)
            self.results[json_data["fullName"]]["results"].sort(key=itemgetter("stop"))
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
        for test in self.results:
            res = self.results[test]["results"]
            status_list = [r["status"].lower() for r in res]
            failures = status_list.count("failed") + status_list.count("broken")
            self.results[test]["failure_rate"] = int(
                Decimal(failures / status_list.__len__()) * 100
            )

    def create_aggregated_json(self):
        with open(self.output_results_file, "w") as file:
            json.dump(self.results, file, indent=4, sort_keys=True)
        print()
        print("Results saved in {0}".format(self.output_results_file))

    def get_existing_results(self):
        if Path(self.output_results_file).is_file():
            with open(self.output_results_file, "r") as json_file:
                self.results = json.load(json_file)

        for test in self.results:
            for result in self.results[test]["results"]:
                self.existing_uuids.append(result["uuid"])
