# Use a Raspberry Pi compatible base image with Python 3.12
FROM python:3.12
ENV PYTHONUNBUFFERED 1

# Clone and install rpitx
RUN mkdir /opt/rpitx && \
    git clone https://github.com/F5OEO/rpitx /opt/rpitx && \
    cd /opt/rpitx && \
    ./install.sh

# Copy the Python application files into the container
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy the rest of the application files
WORKDIR /app
COPY src/main.py main.py

# add RPItx to path
ENV PATH="$PATH:/opt/rpitx"

# Set the entry point for the container
CMD ["python", "main.py"]
