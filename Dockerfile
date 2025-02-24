FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl

RUN groupadd -g 1001 vis-server
RUN useradd -u 1001 -g 1001 -m vis-server
RUN id vis-server

USER 1001
RUN mkdir -p /home/vis-server/app
WORKDIR /home/vis-server/app

COPY requirements.txt /home/vis-server/app/requirements.txt
USER 0
RUN pip3 install -r requirements.txt
USER 1001

COPY --chown=1001:1001 .streamlit /home/vis-server/app/.streamlit
COPY --chown=1001:1001 main.py /home/vis-server/app/main.py
COPY --chown=1001:1001 welcome /home/vis-server/app/welcome
COPY --chown=1001:1001 entrypoint.sh /home/vis-server/app/entrypoint.sh
COPY --chown=1001:1001 analysis /home/vis-server/app/analysis

EXPOSE 8501

RUN chmod +x /home/vis-server/app/entrypoint.sh
ENTRYPOINT ["/home/vis-server/app/entrypoint.sh"]