# Build stage

FROM node:21.7.1-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev

COPY . .
RUN npm run build

# Production stage
FROM nginx:1.25.4-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80

