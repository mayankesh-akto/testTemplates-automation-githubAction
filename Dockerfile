FROM alpine:3.10

WORKDIR /app

COPY ./action.yaml /app/action.yaml
COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirement.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV GITHUB_ACCESS_TOKEN ${{ inputs.github-access-token }}
ENV EMAIL_RECIPIENT ${{ inputs.email-recipient }}
ENV SMTP_USERNAME ${{ inputs.smtp-username }}
ENV SMTP_PASSWORD ${{ inputs.smtp-password }}

CMD ["python", "/app/main.py"]
