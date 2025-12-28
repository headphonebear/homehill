FROM alpine:latest

# Installiere Docker-CLI (und curl, falls nötig für Debugging)
RUN apk add --no-cache docker-cli

# Dein Prune-Skript als CMD
CMD ["sh", "-c", "while true; do docker container prune -f --filter 'until=60m'; sleep 3600; done"]
