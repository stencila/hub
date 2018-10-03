FROM node:8

RUN useradd -ms /bin/bash textilla
WORKDIR /home/textilla
USER textilla

COPY package.json .
RUN npm install --production

ADD --chown=textilla:textilla . .

CMD ["npm", "start"]
