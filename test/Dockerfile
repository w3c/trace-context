FROM python:3

WORKDIR /usr/src/app
RUN pip install --no-cache-dir aiohttp
COPY . .

EXPOSE 7777

CMD python ./self_test.py
