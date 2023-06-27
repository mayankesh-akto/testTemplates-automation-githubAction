import os
import csv
import requests
import yaml
from github import Github


REPOSITORY_OWNER = 'akto-api-security'
REPOSITORY_NAME = 'akto'
BRANCH_NAME = 'master'
FOLDER_PATH = 'apps/dashboard/src/main/resources/inbuilt_test_yaml_files'
FILE_EXTENSION = '.yaml'

CSV_FILE_PATH = 'test.csv'


def fetch_yaml_data(access_token, yaml_url):
    g = Github(access_token)

    repository_parts = yaml_url.replace("https://github.com/", "").split("/")
    file_path = f"{FOLDER_PATH}/{repository_parts[-1]}"

    repository = g.get_repo(f"{REPOSITORY_OWNER}/{REPOSITORY_NAME}")

    try:
        content_of_file = repository.get_contents(file_path)
        data = content_of_file.decoded_content.decode("utf-8")
        yaml_data = yaml.safe_load(data)
        print(f"Successfully fetched the template: {repository_parts[-1]}")
        return yaml_data, data
    except Exception as e:
        print(f"Failed to fetch YAML data for {repository_parts[-1]}")
        print(f"Error: {str(e)}")
        return None, None


def write_to_csv(csv_writer, yaml_data, yaml_content):
    column = []
    column.append(yaml_data['info']['name'])
    column.append(yaml_data['info']['name'])
    column.append(yaml_data['info']['description'])
    column.append(yaml_data['info']['details'])
    column.append(yaml_data['info']['impact'])
    column.append(yaml_data['info']['category']['displayName'])
    column.append(yaml_data['info']['severity'])

    if 'references' in yaml_data['info']:
        column.append(yaml_data['info']['references'])
    else:
        column.append("")

    column.append(yaml_content)

    url_path = ''
    column.append(url_path)

    csv_writer.writerow(column)


def fetch_yaml_files(api_url, access_token):
    try:
        response = requests.get(api_url, headers={'Authorization': f'Bearer {access_token}'})
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve the repository contents.")
    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching repository contents.")
        print(f"Error: {str(e)}")
    return None


def fetch_all_yaml(api_url, access_token, csv_file_path):
    yaml_files = fetch_yaml_files(api_url, access_token)
    if yaml_files:
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Name', 'Slug', 'Description', 'Details', 'Impact', 'OWASP Category', 'Severity', 'References', 'Content', 'URL Path'])

            for yaml_file in yaml_files:
                yaml_url = yaml_file['html_url']
                yaml_data, yaml_content = fetch_yaml_data(access_token, yaml_url)
                if yaml_data:
                    write_to_csv(writer, yaml_data, yaml_content)
        print(f"CSV file '{csv_file_path}' has been generated successfully.")


def main():
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    api_url = f'https://api.github.com/repos/{REPOSITORY_OWNER}/{REPOSITORY_NAME}/contents/{FOLDER_PATH}?ref={BRANCH_NAME}'
    fetch_all_yaml(api_url, access_token, CSV_FILE_PATH)


if __name__ == "__main__":
    main()
