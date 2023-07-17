FROM python:latest

WORKDIR /home/management_bot

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "-O", "main.py"]
