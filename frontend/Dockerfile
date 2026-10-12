# --- Stage 1: Build der Flutter Web-App ---
FROM debian:latest AS builder

# Build-Argument deklarieren
ARG BACKEND_URL
ENV BACKEND_URL=${BACKEND_URL}

RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash flutteruser
USER flutteruser
WORKDIR /home/flutteruser

RUN git clone https://github.com/flutter/flutter.git /home/flutteruser/flutter
ENV PATH="/home/flutteruser/flutter/bin:/home/flutteruser/flutter/bin/cache/bin:$PATH"
RUN flutter config --enable-web

WORKDIR /app

COPY --chown=flutteruser:flutteruser pubspec.yaml ./
RUN flutter pub get

COPY --chown=flutteruser:flutteruser . .

RUN flutter create . --platforms web

# WICHTIG: Die Variable hier an den Dart-Compiler übergeben!
RUN flutter build web --release --dart-define=BACKEND_URL=${BACKEND_URL}


# --- Stage 2: Auslieferung über Nginx ---
FROM nginx:alpine

COPY --from=builder /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]