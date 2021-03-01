FROM alpine
RUN apk add --no-cache curl unzip
COPY groundsman.sh .
ENTRYPOINT groundsman.sh
