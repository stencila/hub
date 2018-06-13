FROM node:8

RUN useradd -ms /bin/bash editor
WORKDIR /home/editor
USER editor

COPY package.json .
RUN npm install

ADD . .

CMD ["npm", "start"]
