# Frontend Dockerfile
#
# Two-stage build:
# Stage 1: Build the React app (produces static HTML/CSS/JS files)
# Stage 2: Serve those files with nginx (a lightweight web server)
#
# Why two stages? The build tools (Node, npm) are ~1GB but the output
# is just ~2MB of static files. No need to ship Node in production.

# Stage 1: Build
FROM node:20-alpine AS build
WORKDIR /app
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=$VITE_API_BASE
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
