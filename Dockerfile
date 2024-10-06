# Use a Raspberry Pi compatible base image with Python 3.12
FROM python:3.12

# Set the working directory
WORKDIR /app

# Clone and install rpitx
RUN git clone https://github.com/F5OEO/rpitx \
    cd rpitx \
    ./install.sh

# Copy the Python application files into the container
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Copy the rest of the application files
COPY src/main.py .

# add RPItx to path
ENV PATH="$PATH:/app/rpitx"

# Set the entry point for the container
CMD ["python", "/app/main.py"]
