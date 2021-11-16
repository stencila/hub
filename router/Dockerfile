FROM nginx:1.21.4

RUN apt-get update \
 && apt-get install -y \
      apache2-utils \
 && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/nginx.conf.template
COPY *.html /usr/share/nginx/html/
COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
