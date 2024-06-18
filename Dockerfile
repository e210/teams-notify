FROM python:3.12-slim

# install requirements
COPY requirements.txt /
WORKDIR /
RUN pip install --no-cache-dir -r requirements.txt

# copy the pipe source code
COPY pipe.yml LICENSE.txt README.md /
COPY pipe /

ENTRYPOINT ["python3", "/pipe.py"]
