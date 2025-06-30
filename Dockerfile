# Use a standard, lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# IMPORTANT: Set an environment variable placeholder for the API key.
# The actual key will be passed in during the 'docker run' command for security.
ENV GOOGLE_API_KEY=""

# Expose the port the app will run on
EXPOSE 8000

# The command to run the application when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]