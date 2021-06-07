FROM python:3.9

WORKDIR /bot

COPY requirements-pypa.txt /tmp
RUN python3.9 -m venv /opt/litebot/venv \
 && /opt/litebot/venv/bin/python -m pip install --no-deps --require-hashes -r /tmp/requirements-pypa.txt \
 && rm /tmp/requirements-pypa.txt

COPY requirements.txt /tmp
RUN /opt/litebot/venv/bin/python -m pip install --no-deps --require-hashes -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt

COPY plugins ./plugins
COPY _plugin_deps.py .
RUN python3.9 _plugin_deps.py

COPY . .

CMD ["/opt/litebot/venv/bin/python", "-m","litebot"]
