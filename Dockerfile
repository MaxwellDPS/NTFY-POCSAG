# Use a Raspberry Pi compatible base image with Python 3.12
FROM dtcooper/raspberrypi-os:python3.12
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/rpitx

# Clone and install rpitx
RUN apt update -y && apt install -y \
    libsndfile1-dev \
    git \
    imagemagick \
    libfftw3-dev \
    libraspberrypi-dev \
    rtl-sdr \
    buffer

RUN git clone https://github.com/F5OEO/rpitx /opt/rpitx

RUN git clone https://github.com/F5OEO/librpitx /opt/rpitx/src/librpitx && \
    cd /opt/rpitx/src/librpitx/src  && \
    make && make install

RUN cd /opt/rpitx/src && \
    make ../pocsag 

# Install pocsag to the path
RUN install /opt/rpitx/pocsag /usr/local/bin/pocsag

# Copy the Python application files into the container
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

WORKDIR /app

# Copy the rest of the application files
COPY src/main.py main.py

# Set the entry point for the container
CMD ["python", "main.py"]
