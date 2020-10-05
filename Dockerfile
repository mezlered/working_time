FROM python:3.6
WORKDIR /app
COPY working_time.py .
ENTRYPOINT ["python", "working_time.py"]