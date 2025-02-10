FROM node:18-alpine

WORKDIR /app

# Enable corepack and set up yarn
RUN corepack enable && corepack prepare yarn@4.6.0 --activate

COPY package.json yarn.lock ./
COPY .yarn ./.yarn
COPY .yarnrc.yml ./

# Install dependencies
RUN yarn install

COPY . .
RUN yarn build

EXPOSE 3000
ENV NODE_ENV=production

CMD ["yarn", "start"] 