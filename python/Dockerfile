FROM python:3.8
# set env for python
ENV PYTHONUNBUFFERED 1
# create dir for ssh keys
RUN mkdir -p /root/.ssh
# copy ssh private key
COPY /keys/id_rsa /root/.ssh/
# copy ssh public key
COPY /keys/id_rsa.pub /root/.ssh/
# Create app directory
RUN mkdir -p /app
# change default dir
WORKDIR /app
# Change ENV for PATH
ENV PATH="/app:${PATH}"
# Install netmiko on the container
RUN pip3 install netmiko