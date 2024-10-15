FROM python:3.12

COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src .
CMD ["python", "main.py"]