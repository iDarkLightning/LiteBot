import os

PIP_INSTALL = "python3.9 -m venv /opt/litebot/venv && /opt/litebot/venv/bin/python -m pip install -r {}"
PLUGINS_DIR = os.path.join(os.getcwd(), "plugins")

def main():
    reqs = []

    for root, dirs, files in os.walk(PLUGINS_DIR):
        for file in files:
            if file == "requirements.txt":
                reqs.append(os.path.join(root, file))

    if reqs:
        for req in reqs:
            os.system(PIP_INSTALL.format(req))

if __name__ == "__main__":
    main()
