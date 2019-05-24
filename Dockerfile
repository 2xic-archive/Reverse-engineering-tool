FROM python:3-slim

WORKDIR /app

COPY . /app

#RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN chmod +x ./install.sh
RUN ./install.sh
EXPOSE 80

ENTRYPOINT ["python", "web.py"]

#	docker build --tag=reverse .
#	docker run -p 4000:80 reverse ./test_binaries/fibonacci
#	docker run -it --entrypoint /bin/bash reverse


