FROM python:3.6-alpine
COPY . /app
WORKDIR /app
RUN apk update && apk add gcc python3-dev musl-dev coreutils
RUN pip install -r requirements.txt
EXPOSE 5678
CMD ["python", "app.py"]
