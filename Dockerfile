FROM python:3

RUN pip install kodi-json prometheus_client
ADD kodi_exporter.py /usr/local/bin/kodi_exporter
RUN chmod 755 /usr/local/bin/kodi_exporter

ENV PROMETHEUS_PORT=9100
ENV KODI_URL="http://localhost/jsonrpc"

CMD kodi_exporter
