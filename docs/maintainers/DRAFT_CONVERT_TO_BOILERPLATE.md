# Convert to Boilerplate [DRAFT]

1. Create a feature branch from `main-boilerplate`
2. Merge `main` branch into this feature branch
   - IGNORE ALL THE MERGE CONFLICTS - JUST OVERRIDE EVERYTHING WITH THE FILES FROM MAIN BRANCH (`cp -r backup/* .` and `cp -r backup/.* .` but DO DELETE `.git` folder from the backup directory first)
3. Create a feature branch from this feature branch ?
4. Delete `claude_code_proxy` folder
5. Delete `docs/DOCKER_PUBLISHING.md`
   - TODO Advice to check against similar section(s) in `README_BOILERPLATE.md` first
6. Delete `images/claude-code-gpt-5.jpeg`
7. Delete `deploy-docker.sh`
8. Delete `kill-docker.sh`
9. Delete `run-docker.sh`
10. Override `README.md` with `README_BOILERPLATE.md`
11. Restore this note at the top of this new README:
    ```markdown
    > **NOTE:** If you want to go back to the `Claude Code CLI Proxy` version of this repository, click [here](https://github.com/teremterem/claude-code-gpt-5).
    ```
12. Restore `docs/DOCKER_TIPS.md` as it was in the `main-boilerplate` branch
    - TODO Advice to read both variants first, though - just to see if there is anything useful in the non-boilerplate version that might make sense to incorporate into the boilerplate version
13. Restore `.env.template` as it was in the `main-boilerplate` branch
    - TODO Advice to review both first...
14. Same with `config.yml`
15. Same with `docker-compose.dev.yml` (or maybe just fix service and container names)
16. Same with `docker-compose.yml`
17. Remove `claude-code-gpt-5` related labels from `Dockerfile`
18. Fix name and description in `pyproject.toml` (take them from boilerplate version)
19. [NOTE: PROBABLY SHOULD NOT BE DONE, BECAUSE `X.X.X-bpX` VERSION FORMAT IS NOT SUPPORTED IN `pyproject.toml`] ~~Update version too~~
20. Run `uv lock` to regenerate `uv.lock` file (do not use `--upgrade` flag - that's meant to be done while still developing in regular `main` branch)
21. Restore `uv-run.sh` as it was in the `main-boilerplate` branch
    - TODO Advice to review both first...
22. Just fully override content of `common/`, `yoda_example/` and `librechat/` with what comes from regular `main` branch (just let it happen by itself, in other words)
    - TODO Still advice to review both versions of each folder first...
23. TODO Make the reader think if anything else needs to be done
24. Delete `docs/CONVERT_TO_BOILERPLATE.md`
25. SQUASH and merge the feature of the feature branch into the feature branch
26. Test the project
27. Merge this feature branch into `main-boilerplate` (DO NOT SQUASH, JUST MERGE!)
28. Tag new version
29. Publish TWO new images to GitHub Container Registry:
    - `ghcr.io/teremterem/litellm-server-yoda:<version>`
    - `ghcr.io/teremterem/litellm-server-yoda:latest`
    - `ghcr.io/teremterem/librechat-yoda:<version>`
    - `ghcr.io/teremterem/librechat-yoda:latest`
