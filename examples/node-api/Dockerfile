# Dockerfile com problemas propositais para demonstrar o SmartDocker
FROM node:latest

WORKDIR /app

ENV API_KEY=sk-exemplo-1234567890

COPY . .

RUN apt-get update && apt-get install -y curl vim git

RUN npm install

EXPOSE 8080

CMD ["npm", "start"]
