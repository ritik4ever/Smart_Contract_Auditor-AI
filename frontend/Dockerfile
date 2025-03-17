version: '3'

services:
backend:
build:
context: ./backend
dockerfile: Dockerfile
ports:
- "5000:5000"
environment:
- MODEL_PATH=gpt2
- PORT=5000
volumes:
- ./backend:/app
deploy:
resources:
limits:
memory: 4G
restart: unless-stopped

frontend:
build:
context: ./frontend
dockerfile: Dockerfile
ports:
- "80:80"
depends_on:
- backend
restart: unless-stopped