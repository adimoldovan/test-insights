import json
from datetime import datetime

from mako.template import Template

INPUT_RESULTS_FILE = '../demo/results.json'
OUTPUT_REPORT_FILE = '../demo/report.html'
OUTPUT_TEMPLATE_FILE = '../resources/template.html'


def generate_html():
    with open(INPUT_RESULTS_FILE, 'r') as json_file:
        results = json.load(json_file)

    template = Template(filename=OUTPUT_TEMPLATE_FILE)
    with open(OUTPUT_REPORT_FILE, 'w') as html_file:
        output = template.render(data=results, generated_date=datetime.now().isoformat())
        # print(output)
        html_file.write(output)
    print()
    print('Report saved in {0}'.format(OUTPUT_REPORT_FILE))


def main():
    generate_html()


if __name__ == "__main__":
    main()
