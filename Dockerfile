FROM python:3.9-slim

RUN useradd -r -m worker
USER worker
WORKDIR /home/worker
COPY --chown=worker requirements.txt .
RUN pip install --user -r requirements.txt
COPY --chown=worker . .

CMD ["python3", "main.py"]


