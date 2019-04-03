FROM python:3.7-alpine

CMD apk add build-base

COPY etherscan-exporter /exporter/etherscan-exporter
COPY etherscan /exporter/etherscan
COPY requirements.txt /exporter/requirements.txt

RUN pip install -r /exporter/requirements.txt

WORKDIR /exporter

EXPOSE 9998

ENTRYPOINT ["python", "/exporter/etherscan-exporter"]