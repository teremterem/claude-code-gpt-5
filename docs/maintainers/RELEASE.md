# Release Process

This guide is intended for the maintainers of the Claude Code GPT-5 repository to release a new version of the Claude Code GPT-5 Proxy. The starting point of this guide is the moment after all the relevant changes have been merged into the `main` branch (being tested before the merge, of course).

1. Make sure you are on the `main` branch:

   ```bash
   git switch main
   git pull
   git status
   ```

2. **Test the `main` branch after all the final merges and/or commits were done.**

3. **Prepare and release the Boilerplate version of the project by following the steps in `docs/maintainers/CONVERT_TO_BOILERPLATE.md` from the beginning to the end before coming back to this guide.**

4. Make sure you are back on the `main` branch:

   ```bash
   git switch main
   git pull
   git status
   ```

## Create a new release in GitHub

5. Tag the new version and push the tags to the remote repository:

   ```bash
   git tag -a X.X.X  # Replace with the actual version number
   ```

   ```bash
   git push --tags
   git status
   ```

6. Go to the GitHub Releases page and create a new release:

   - **Title:** `X.X.X`
   - **Description:** \<release notes\>
   - **Discussion:** create a new discussion
   - **Mark as latest:** TRUE

## Publish a Docker image to GHCR

### Prerequisites

- A GitHub [Personal Access Token (PAT)](https://github.com/settings/tokens) with the `write:packages` scope
- Docker installed on your machine
- Multi-arch `buildx` enabled in Docker (see [Docker documentation](https://docs.docker.com/build/install-buildx/))

### Steps

7. Login to GHCR:

   ```bash
   # Replace <GITHUB_PAT> and <GITHUB_USERNAME>
   echo <GITHUB_PAT> | docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin
   ```

8. Build the Docker image and push it to GHCR:

   ```bash
   docker buildx build \
     --platform linux/amd64,linux/arm64 \
     -t ghcr.io/teremterem/claude-code-gpt-5:<X.X.X> \  # Replace <X.X.X>
     -t ghcr.io/teremterem/claude-code-gpt-5:latest \
     --push .
   ```

   > **NOTE:** If publishing for the first time, then, after you published it with the command above, make sure to make the package public in [GHCR package settings](https://github.com/users/teremterem/packages/container/claude-code-gpt-5/settings) and also [connect it to the project repository](https://github.com/users/teremterem/packages/container/package/claude-code-gpt-5).

9. **Test the published Docker image by running the `run-docker.sh` ( and/or `deploy-docker.sh`) script.**

---

That's it! You have released a new version of the Claude Code GPT-5 Proxy and published the Docker image to GHCR.
