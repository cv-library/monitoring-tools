FROM python:3.10-slim-buster 

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN mkdir /db
RUN groupadd --gid 1000 cron-exporter \
    && useradd --uid 1000 --gid cron-exporter --shell /bin/bash --create-home cron-exporter

RUN chown cron-exporter:cron-exporter /app -R && \
    chown cron-exporter:cron-exporter /db -R

EXPOSE 5902

#USER cron-exporter

CMD ["python", "main.py"]

