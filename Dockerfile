FROM alpine:3.10

COPY requirements.txt /requirements.txt 
COPY main.py /main.py

RUN apk update
RUN apk add --no-cache python3 python3-dev libffi-dev
RUN apk add --no-cache py3-pip
RUN apk add --no-cache build-base 
RUN python3 -m virtualenv /venv
RUN source /venv/bin/activate
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools wheel
RUN pip3 install --no-cache-dir virtualenv
RUN pip3 install --no-cache-dir -r /requirements.txt

CMD ["/venv/bin/python3", "/main.py"]