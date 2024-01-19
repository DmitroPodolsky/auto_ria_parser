FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /app/bot
COPY . .
RUN pip install -r requirements.txt
CMD ["python","-m","app"]
