# Use a Raspberry Pi compatible base image with Python 3.12
FROM python:3.12

# Install required packages for building rpitx
RUN apt-get update && \
    apt-get install -y git build-essential cmake wiringpi

# Set the working directory
WORKDIR /app

# Clone and install rpitx
RUN curl -sL https://raw.githubusercontent.com/F5OEO/rpitx/refs/heads/master/install.sh | sh 

# Copy the Python application files into the container
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Copy the rest of the application files
COPY src/main.py .

# Set GPIO permissions (needed to use rpitx properly)
RUN chmod +x /dev/gpiomem /dev/mem 

# Set the entry point for the container
CMD ["python", "/app/main.py"]
