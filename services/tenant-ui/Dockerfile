FROM node:24-alpine

WORKDIR /usr/src/app

# Copy only the dependency manifests first so the npm ci layers
# stay cached as long as the lockfiles don't change
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package-lock.json ./frontend/

# install backend libs (clean the npm cache in the same layer so it isn't committed to the image)
RUN npm ci && npm cache clean --force
# install frontend libs
RUN cd frontend && npm ci && npm cache clean --force

# Copy in the source - code changes only invalidate layers from here down
COPY . .

# build backend
RUN npm run build
# build frontend
RUN cd frontend && npm run build
# these are not needed now, save some space
RUN rm -rf frontend/node_modules

EXPOSE 8080
CMD [ "node", "--enable-source-maps", "dist/src/index.js" ]
