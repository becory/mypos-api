FROM python:3.8-slim
ENV TZ=Asia/Taipei
RUN pip3 install --upgrade pip setuptools
RUN pip3 install psycopg2-binary

EXPOSE 8000
WORKDIR /app/api
COPY requirements.txt /app/api
COPY secret_key.txt /app/api
RUN pip3 install -r requirements.txt
COPY . /app/api/
ENTRYPOINT ["python3"]
#CMD ["ls"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]