FROM alpine
RUN apk add --no-cache curl unzip
COPY groundsman.sh .

