FROM python:3.8
# set env for python
ENV PYTHONUNBUFFERED 1
# Create app directory
RUN mkdir -p /app
# change default dir
WORKDIR /app
# Change ENV for PATH
ENV PATH="/app:${PATH}"
# Install netmiko on the container
RUN pip3 install netmiko