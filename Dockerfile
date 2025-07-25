FROM python:3-slim

WORKDIR /action

COPY ./Pipfile* ./
RUN pip install pipenv && \
  pipenv install --system --deploy && \
  pipenv --clear

COPY ./src ./src
COPY ./main.py .

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]