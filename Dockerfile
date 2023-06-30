FROM alpine:3.10

WORKDIR /app

COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirements.txt

RUN apk update
RUN apk add --no-cache python3 python3-dev
RUN apk add --no-cache py3-pip
RUN apk add --no-cache build-base 
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools wheel
RUN pip3 install --no-cache-dir -r /app/requirements.txt

ENV GITHUB_ACCESS_TOKEN ${{ inputs.github-access-token }}
ENV EMAIL_RECIPIENT ${{ inputs.email-recipient }}
ENV SMTP_USERNAME ${{ inputs.smtp-username }}
ENV SMTP_PASSWORD ${{ inputs.smtp-password }}

CMD ["python3", "/app/main.py"]
