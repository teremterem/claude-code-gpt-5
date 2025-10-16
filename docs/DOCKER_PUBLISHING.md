# Publishing your LiteLLM Server to GHCR

## Prerequisites

- A GitHub [Personal Access Token (PAT)](https://github.com/settings/tokens) with the `write:packages` scope
- Docker installed on your machine
- Multi-arch `buildx` enabled in Docker (see [Docker documentation](https://docs.docker.com/build/install-buildx/))

## Steps

1. **Login to GHCR:**

```bash
echo <YOUR_GITHUB_PAT> | docker login ghcr.io -u <YOUR_GITHUB_USERNAME> --password-stdin
```

2. **Build the Docker image and push it to GHCR:**

TODO Make it clear that the registry URL should be changed to your own

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/teremterem/my-litellm-server:<VERSION> \
  -t ghcr.io/teremterem/my-litellm-server:latest \
  --push .
```

> **NOTE:** It could also be built with regular `docker build` but then it would not work for both, ARM-based platforms like Apple Silicon and Intel/AMD-based ones, simultaneously.
