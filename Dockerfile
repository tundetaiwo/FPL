# Start your image with a node base image
FROM ubuntu:latest

WORKDIR /app

RUN : \
	&& apt update \
	&& apt install -y python3 \
	&& apt install -y pipx \
	&& pipx ensurepath \
	&& pipx install poetry==1.8.0 \
	&& :



