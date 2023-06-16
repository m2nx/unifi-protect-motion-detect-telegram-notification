# Base image
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Copy the script into the container
COPY . .

# Install any necessary libraries
RUN pip install -r requirements.txt
# Run the script

CMD ["python", "main.py"]
