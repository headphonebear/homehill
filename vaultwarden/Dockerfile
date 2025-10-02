FROM vaultwarden/server:latest

# Füge ein Entrypoint-Script hinzu, das das Secret liest und in ADMIN_TOKEN setzt
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'export ADMIN_TOKEN=$(cat /run/secrets/vaultwarden_admin_token)' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/vaultwarden"]
