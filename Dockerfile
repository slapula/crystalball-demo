FROM python:3.7
WORKDIR /usr/src/app
RUN pip install -U boto3 kubernetes
COPY . .
CMD ["python", "./main.py"]
