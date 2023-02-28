FROM artifactory.chrobinson.com:5050/datascience/datascience-python37:latest

RUN groupadd -r app &&\
    useradd -r -g app -d /usr/src/app -s /sbin/nologin -c "DockerUser" app && \
    mkdir -p /usr/src/app && \
    chown app /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /app
WORKDIR /app
USER app

EXPOSE 8050

CMD [ "python" , "lms_app/app.py"]