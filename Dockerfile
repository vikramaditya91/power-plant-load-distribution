FROM python:3.6

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN python -m pip install -r requirements.txt
ENV PYTHONPATH /app
COPY . /app

#ENTRYPOINT [ "/bin/bash" ]
CMD ["python3", "app/manage.py", "run"]

