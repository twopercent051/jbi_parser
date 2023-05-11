FROM python:3.10

RUN mkdir /jbi_parser

WORKDIR /jbi_parser

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python3