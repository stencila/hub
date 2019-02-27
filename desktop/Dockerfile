FROM node:8

RUN useradd -ms /bin/bash desktop
WORKDIR /home/desktop
USER desktop

COPY package.json .
RUN npm install --production

ADD --chown=desktop:desktop . .

CMD ["npm", "start"]
