FROM python:3.9-slim

WORKDIR /graph_ql
COPY . .

RUN apt-get update && apt-get install make
RUN make requirements

EXPOSE 8000

ENTRYPOINT [ "make", "server" ]
