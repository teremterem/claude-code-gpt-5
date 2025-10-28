# Publishing Claude Code GPT-5 Proxy to GHCR (Maintainer's Guide)

This guide is intended for the maintainers of the Claude Code GPT-5 repository to build and publish the Docker image to GitHub Container Registry (GHCR). **If you are simply looking to use the Docker image, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) instead.**

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

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/teremterem/claude-code-gpt-5:<VERSION> \
  -t ghcr.io/teremterem/claude-code-gpt-5:latest \
  --push .
```

> **NOTE:** If publishing for the first time, then, after you published it with the command above, make sure to make the package public in [GHCR package settings](https://github.com/users/teremterem/packages/container/claude-code-gpt-5/settings) and also [connect it to the project repository](https://github.com/users/teremterem/packages/container/package/claude-code-gpt-5).
