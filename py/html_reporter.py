import json
import os
import shutil
from datetime import datetime
from pathlib import Path

import htmlmin
from mako.template import Template


class HTMLReporter:
    def __init__(self, config):
        self.json_report = os.path.join(
            config["output"]["dir"], config["output"]["json"]
        )
        self.resources_dir = "resources"
        self.html_report = self.output_results_file = os.path.join(
            config["output"]["dir"], config["output"]["html"]
        )

    def report(self):
        # Get the JSON report data
        with open(self.json_report, "r") as json_file:
            results = json.load(json_file)

        print(os.getcwd())

        template = Template(filename=os.path.join(self.resources_dir, "template.html"))

        # Create output dir
        Path(Path(self.html_report).parent).mkdir(parents=True, exist_ok=True)

        # Write the HTML report
        with open(self.html_report, "w") as html_file:
            output = template.render(
                data=results, generated_date=datetime.now().isoformat()
            )
            html_file.write(
                htmlmin.minify(
                    output,
                    remove_comments=True,
                    remove_empty_space=True,
                    remove_all_empty_space=True,
                )
            )

        print()
        print("Report saved in {0}".format(self.html_report))

        # Move resources (css, js) with the HTML report
        output = Path(self.html_report).parent

        for f in ["list.min.js", "insights.css", "insights.js"]:
            shutil.copy(os.path.join(self.resources_dir, f), os.path.join(output, f))
