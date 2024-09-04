import base64
import requests
import configparser
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import numpy as np
from io import BytesIO
import os
import logging
from logging.handlers import RotatingFileHandler
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import calendar

# Read configuration from the conf.ini file
def read_config():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    return config

# Fetch data from JIRA using the provided credentials
def fetch_jira_data():
    config = read_config()
    jira_info = config['JIRA']
    url = jira_info['url']
    user = jira_info['user']
    token = jira_info['token']
    default_reports = jira_info['defaultReports'].split(',')

    auth_str = f"{user}:{token}"
    auth_header = f"Basic {base64.b64encode(auth_str.encode()).decode()}"

    reports_data = {}
    for report_id in default_reports:
        response = requests.get(f"{url}{report_id}", headers={'Authorization': auth_header})
        if response.status_code == 200:
            reports_data[report_id] = response.json()
        else:
            print(f"Failed to fetch report {report_id}")

    return reports_data

class Set:
    """
    Set - helper class, contains one set of a series.
    """

    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.x = list()
        self.y = list()
        self.avg = 0
        self.cnt = 0
        self.type = None

    def calcMetrics(self):
        """
        calcMetrics() - a function to calculate the count and the average of all values to the set y values
        """
        for elem in self.y:
            self.cnt = self.cnt + elem
        self.avg = self.cnt / len(self.y)

class Report:
    """
    Report - helper class contains all the series in a report
    """

    def __init__(self, name):
        self.name = name
        self.series = list()

    def addSet(self, set):
        """
        addSet - addes a set to the serries
        """
        set.calcMetrics()
        self.series.append(set)

def initLogger(logFile):
    logging.basicConfig(
        handlers=[RotatingFileHandler(logFile, maxBytes=1000000, backupCount=5)],
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')
    log = logging.getLogger("JIRAREPORTS")
    log.setLevel(logging.DEBUG)

    return log

def generate_graphs(reports_data):
    graphs = {}

    for report_id, data in reports_data.items():
        categories = data.get('categories')
        values = data.get('values')

        if categories is None or values is None:
            print(f"Skipping report {report_id} due to missing data")
            continue

        x = np.arange(len(categories))

        plt.bar(x, values)
        plt.xlabel('Categories')
        plt.ylabel('Values')
        plt.title('Sample Graph')

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        plt.close()

        graphs[report_id] = img_str

    return graphs

def write_to_file(formatted_data, graphs):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('report_template.html')
    with open('jira_report.html', 'w') as file:
        file.write(template.render(data=formatted_data, graphs=graphs))

def main():
    dir = os.path.dirname(__file__)
    logFile = os.path.join(dir, 'log', 'JiraReports.log')
    log = initLogger(logFile)
    log.info("JiraReports is starting ...")

    # Fetching data from JIRA
    reports_data = fetch_jira_data()

    # Formatting fetched data
    formatted_data = format_data(reports_data)

    # Generating graphs
    graphs = generate_graphs(reports_data)

    # Writing to file
    write_to_file(formatted_data, graphs)

if __name__ == "__main__":
    main()
