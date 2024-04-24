# # Use an official Python runtime as a parent image
# FROM python:3.9-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install any needed dependencies specified in requirements.txt
# RUN pip3 install --upgrade pip
# RUN pip3 install -r requirements.txt

# # Expose the port your app runs on
# EXPOSE 5000

# Run the API service
#CMD ["python", "api.py"]

# Use an official MySQL runtime as a parent image
FROM mysql:latest

# Set the environment variables
ENV MYSQL_ROOT_PASSWORD="pikapikachu"
ENV MYSQL_DATABASE="dsa3101"

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the SQL script to initialize the database
COPY main.sql /docker-entrypoint-initdb.d/main.sql
