FROM python:3.6.11
# FROM  irons:v1
ENV PYTHONUNBUFFERED 1

# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
# RUN apk add --update --no-cache bash gcc gfortran musl-dev freetype-dev

WORKDIR irons


COPY requirements.txt ./

RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple


COPY models ./models/
COPY ecci_sdk.py ./

COPY pred.py ./

ENTRYPOINT ["python3","pred.py"]
