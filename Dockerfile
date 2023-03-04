FROM  python:3.8-slim
ENV PYTHONBUFFERED 1
RUN apt-get update && apt-get -y install gcc
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN mkdir /app
RUN pip install pip-tools
COPY ./requirements.in /app/requirements.in
RUN pip-compile --upgrade /app/requirements.in
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app