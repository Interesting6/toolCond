FROM python:3.6.11

ENV PYTHONUNBUFFERED 1

# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
# RUN apk add --update --no-cache bash gcc gfortran musl-dev freetype-dev

WORKDIR save

COPY requirements.txt ./
COPY ecci_sdk.py ./
COPY instantclient-basic-linux.x64-11.2.0.4.0.zip ./
COPY libaio.so.1.0.1 /lib/

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && unzip instantclient-basic-linux.x64-11.2.0.4.0.zip \
    && rm -rf instantclient-basic-linux.x64-11.2.0.4.0.zip \
    && ln -s /lib/libaio.so.1.0.1 /lib/libaio.so.1

ENV INSTANCECLIENT_HOME /save/instantclient_11_2
ENV LD_LIBRARY_PATH $INSTANCECLIENT_HOME:$LD_LIBRARY_PATH
ENV PATH $LD_LIBRARY_PATH:$PATH

COPY insert.py ./

ENTRYPOINT ["python3", "insert.py"]