import requests
import json


# Function to fetch graph data from Jira
def fetch_graph_data_from_jira():
    # Update with your Jira instance URL, username, and password/token
    url = 'https://ericsson-service.atlassian.net/jira/servicedesk/projects/CR/reports/custom/27'
    username = 'nir.shoham@ericsson-servoce.com'
    api_token = 'Nirsho81'  # or your password

    headers = {
        'Content-Type': 'application/json',
    }
    # Authorization header with basic authentication
    auth = (username, api_token)

    try:
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise an exception for HTTP errors
        graph_data = response.json()
        return graph_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching graph data: {e}")
        return None


# Function to save graph data to a file
def save_graph_data_to_file(graph_data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(graph_data, file, indent=4)
        print(f"Graph data saved to {file_path}")
    except IOError as e:
        print(f"Error saving graph data to file: {e}")


def main():
    graph_data = fetch_graph_data_from_jira()
    if graph_data:
        save_graph_data_to_file(graph_data, 'graph_data.json')


if __name__ == "__main__":
    main()
