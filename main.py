import os
import csv
import requests
import yaml
import smtplib
from github import Github
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


REPOSITORY_OWNER = 'mayankesh-akto'
REPOSITORY_NAME = 'testing'
BRANCH_NAME = 'main'
FOLDER_PATH = 'app'
FILE_EXTENSION = '.yaml'

EMAIL_RECIPIENT = os.environ['INPUT_EMAIL-RECIPIENT']
EMAIL_SUBJECT = f'CSV Report of {REPOSITORY_OWNER}/{REPOSITORY_NAME}'

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
            print(response.status_code)
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
        send_email(csv_file_path)


def send_email(csv_file_path):
    msg = MIMEMultipart()
    msg['From'] = os.getenv("INPUT_SMTP-USERNAME")
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = EMAIL_SUBJECT

    body = 'Please find the attached CSV report.'
    msg.attach(MIMEText(body, 'plain'))

    with open(csv_file_path, 'rb') as attachment:
        part = MIMEApplication(attachment.read())
        part.add_header('Content-Disposition', 'attachment', filename=csv_file_path)
        msg.attach(part)

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.environ['INPUT_SMTP-USERNAME']
    smtp_password = os.environ['INPUT_SMTP-PASSWORD']

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

    print("Email sent successfully.")


def main():
    access_token = os.environ['INPUT_GITHUB-ACCESS-TOKEN']
    api_url = f'https://api.github.com/repos/{REPOSITORY_OWNER}/{REPOSITORY_NAME}/contents/{FOLDER_PATH}?ref={BRANCH_NAME}'
    fetch_all_yaml(api_url, access_token, CSV_FILE_PATH)


if __name__ == "__main__":
    main()