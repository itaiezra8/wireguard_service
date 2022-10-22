FROM python:3.9-alpine
WORKDIR /code
COPY wireguard /code/wireguard
ADD core /code/core
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install -r  wireguard/requirements.txt
EXPOSE 5010
ENV PYTHONPATH "${PYTHONPATH}:/code"
CMD [ "python", "wireguard/wireguard_server.py"]