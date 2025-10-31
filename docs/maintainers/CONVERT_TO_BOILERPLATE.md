# Converting to Boilerplate (aka My LiteLLM Server)

This guide is intended for the maintainers of the Claude Code GPT-5 repository to derive a "Boilerplate" version of it (aka My LiteLLM Server) upon a new version release. **If you are simply looking to use it as a boilerplate, head over to the [main-boilerplate](https://github.com/teremterem/claude-code-gpt-5/tree/main-boilerplate) branch of this repository and check out the [README](https://github.com/teremterem/claude-code-gpt-5/blob/main-boilerplate/README.md) there.**

## Steps

### Preparation

1. Create a feature branch from `main-boilerplate`
2. Merge `main` branch into this feature branch
   - IGNORE ALL THE MERGE CONFLICTS - JUST OVERRIDE EVERYTHING WITH THE FILES FROM MAIN BRANCH (`cp -r backup/* .` and `cp -r backup/.* .` but DO DELETE `.git` folder from the backup directory first)
3. Create a feature branch from this feature branch ?

### Delete irrelevant parts

4. Delete `docs/DOCKER_PUBLISHING.md`
   - TODO Advice to check against similar section(s) in `README_BOILERPLATE.md` first
5. Delete `docs/CONVERT_TO_BOILERPLATE.md` (and probably the whole `docs/maintainers` folder)
6. Delete `images/claude-code-gpt-5.jpeg`
7. Delete `claude_code_proxy` folder
8. Delete `deploy-docker.sh`
9. Delete `kill-docker.sh`
10. Delete `run-docker.sh`

### Swap README

11. Override `README.md` with `README_BOILERPLATE.md`
12. Restore this note at the top of this new README:
    ```markdown
    > **NOTE:** If you want to go back to the `Claude Code CLI Proxy` version of this repository, click [here](https://github.com/teremterem/claude-code-gpt-5).
    ```

### Bring back certain boilerplate-specific versions of files

13. Restore `docs/DOCKER_TIPS.md` as it was in the `main-boilerplate` branch
    - TODO Advice to read both variants first, though - just to see if there is anything useful in the non-boilerplate version that might make sense to incorporate into the boilerplate version
14. Restore `.env.template` as it was in the `main-boilerplate` branch
    - TODO Advice to review both first...
15. Same with `config.yml`
16. Same with `docker-compose.dev.yml` (or maybe just fix service and container names)
17. Same with `docker-compose.yml`
18. Restore `uv-run.sh` as it was in the `main-boilerplate` branch

### Correct certain parts manually

19. Remove `claude-code-gpt-5` related labels from `Dockerfile`
20. Fix name and description in `pyproject.toml` (take them from boilerplate version)
21. [NOTE: PROBABLY SHOULD NOT BE DONE, BECAUSE `X.X.X-bpX` VERSION FORMAT IS NOT SUPPORTED IN `pyproject.toml`] ~~Update version too~~
22. Run `uv lock` to regenerate `uv.lock` file (do not use `--upgrade` flag - that's meant to be done while still developing in regular `main` branch)
    - TODO Advice to review both first...

### Parts to merge the usual way

23. Just fully override content of `common/`, `yoda_example/` and `librechat/` with what comes from regular `main` branch (just let it happen by itself, in other words)
    - TODO Still advice to review both versions of each folder first...

### Final steps

24. TODO Make the reader think if anything else needs to be done
25. SQUASH and merge the feature of the feature branch into the feature branch
26. Test the project
27. Merge this feature branch into `main-boilerplate` (DO NOT SQUASH, JUST MERGE!)
28. Tag new version
29. Publish TWO new images to GitHub Container Registry:
    - `ghcr.io/teremterem/litellm-server-yoda:<version>`
    - `ghcr.io/teremterem/litellm-server-yoda:latest`
    - `ghcr.io/teremterem/librechat-yoda:<version>`
    - `ghcr.io/teremterem/librechat-yoda:latest`
