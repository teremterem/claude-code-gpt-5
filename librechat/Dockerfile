# This Dockerfile is here for convenience so an image for LibreChat with a
# custom librechat.yaml file can be built and pushed to a registry. This makes
# it easier to deploy LibreChat customizations to various environments, like Azure
# Container Apps, etc. without worrying how to supply a custom librechat.yaml
# file into the container "from the outside".
FROM ghcr.io/danny-avila/librechat:v0.8.0

COPY --chown=node:node librechat.yaml /app/librechat.yaml
