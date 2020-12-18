FROM python:3.9-slim

USER 1234
WORKDIR /app
COPY --chown 1234:1234 requirements.txt /app
RUN pip install --user -r requirements.txt

CMD ["python3", "/app/main.py"]


