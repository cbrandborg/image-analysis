# start by pulling the python image
FROM python:3.12.1-slim-bookworm

ENV PYTHONUNBUFFERED True

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get update -y && \
    apt-get install -y curl gnupg2

# RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-cli -y              

# copy every content from the local file to the image
COPY . /app

EXPOSE 8080

# configure the container to run in an executed manner

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]