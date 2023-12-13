# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set an environment variable with the directory where our app will be installed.
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask to run in production
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run myflaskapp.py when the container launches
CMD ["flask", "run"]
