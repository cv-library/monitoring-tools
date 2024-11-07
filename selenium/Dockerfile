# Use an official Python base image
FROM python:3.10-slim

# Install necessary dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variable to avoid errors with Chrome in headless mode
ENV DISPLAY=:99

# Copy and run the Selenium script
COPY . /app
WORKDIR /app
CMD ["python3", "main.py"]
