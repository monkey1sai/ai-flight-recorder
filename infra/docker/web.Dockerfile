FROM node:22-alpine

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
COPY apps/web ./apps/web
COPY packages/testkit ./packages/testkit
COPY vendor/npm ./vendor/npm

RUN npm install --workspaces --include-workspace-root

CMD ["npm", "run", "dev", "--workspace", "@aeris/web"]
