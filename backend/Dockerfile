FROM python:3.10-bullseye
RUN apt-get update && apt-get install --no-install-recommends -y mupdf-tools

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

COPY . .

