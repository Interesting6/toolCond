FROM python:3.6.11

ENV PYTHONUNBUFFERED 1

# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
# RUN apk add --update --no-cache bash gcc gfortran musl-dev freetype-dev

WORKDIR datasource

COPY requirements.txt ./

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ecci_sdk.py ./
COPY main.py ./


ENTRYPOINT ["python3","main.py"]