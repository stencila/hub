FROM python:3.7

COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

COPY scheduler.py .
CMD celery beat --app scheduler
