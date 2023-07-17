FROM python:latest

RUN apt-get update

CMD ["python", "-O", "main.py"]
