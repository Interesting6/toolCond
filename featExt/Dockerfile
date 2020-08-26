FROM python:3.6.11

ENV PYTHONUNBUFFERED 1

# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
# RUN apk add --update --no-cache bash gcc gfortran musl-dev freetype-dev

WORKDIR featExt

COPY requirements.txt ./

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY feature_extract.py ./
COPY feature_extract_func.py ./
COPY ecci_sdk.py ./

ENTRYPOINT ["python3","feature_extract.py"]