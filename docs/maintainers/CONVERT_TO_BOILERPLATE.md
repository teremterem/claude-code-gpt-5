# Converting to Boilerplate (aka My LiteLLM Server)

This guide is intended for the maintainers of the Claude Code GPT-5 repository to derive a "Boilerplate" version of it (aka My LiteLLM Server) upon a new version release. **If you are simply looking to use it as a boilerplate, head over to the [main-boilerplate](https://github.com/teremterem/claude-code-gpt-5/tree/main-boilerplate) branch of this repository and check out the [README](https://github.com/teremterem/claude-code-gpt-5/blob/main-boilerplate/README.md) there.**

## Steps

> **NOTE:** All the commands below are expected to be run from the root directory of the repository:
```bash
cd <repo-root-dir>
```

### Preparation

0. Backup the content of the `main` branch of the repo to a separate directory:
   ```bash
   rm -ri ../repo-main-backup-dir
   ```
   > **NOTE:** The command above will ask about deleting each and every file. If the directory exists already, this will make you cognizant of this fact. **Retry without `-i` to actually delete it** (no confirmations will be asked).

   Proceed with the backup:
   ```bash
   git switch main
   git pull
   git status
   ```
   ```bash
   cp -r . ../repo-main-backup-dir
   rm -rf ../repo-main-backup-dir/.git
   rm -rf ../repo-main-backup-dir/.venv
   rm ../repo-main-backup-dir/.env
   rm ../repo-main-backup-dir/librechat/.env
   ```

1. Create a feature branch from `main-boilerplate`:
   ```bash
   git switch main-boilerplate
   git pull
   git status
   ```
   > ⚠️ **ATTENTION** ⚠️ If `boilerplate-merging-branch` branch already exists, first make sure to delete it both - locally and from the remote.
   ```bash
   git switch --create boilerplate-merging-branch
   ```
   ```bash
   git push --set-upstream origin boilerplate-merging-branch
   ```

3. Merge `main` branch into this feature branch in the following way:

   2.1 Switch to the feature branch and **initiate the merge** of the `main`:
    ```bash
    git switch boilerplate-merging-branch
    git pull
    git status
   ```
   ```bash
    git merge origin/main
    git status
    ```

   2.2 **IGNORE ALL THE MERGE CONFLICTS** - just override everything with the files that you put away to the temporary directory and conclude the merge:
   ```bash
   cp -r ../repo-main-backup-dir/* .
   cp -r ../repo-main-backup-dir/.* .
   git add --all
   git status
   ```
   ```bash
   git commit -m 'Merge remote-tracking branch '\''origin/main'\'' into boilerplate-merging-branch'
   git push
   git status
   ```

4. Create **a feature branch from the feature branch:**
   ```bash
   git switch boilerplate-merging-branch
   git pull
   git status
   ```
   > ⚠️ **ATTENTION** ⚠️ If `boilerplate-MANUAL-merging-branch` branch already exists, first make sure to delete it both - locally and from the remote.
   ```bash
   git switch --create boilerplate-MANUAL-merging-branch
   ```
   ```bash
   git push --set-upstream origin boilerplate-MANUAL-merging-branch
   ```

### Delete irrelevant files

4. Delete the following files and folders, as they are not supposed to be part of the boilerplate:
   ```bash
   git switch boilerplate-MANUAL-merging-branch
   git pull
   git status
   ```
   ```bash
   rm -rf claude_code_proxy/
   rm docs/maintainers/DOCKER_PUBLISHING.md
   rm docs/maintainers/CONVERT_TO_BOILERPLATE.md
   rm images/claude-code-gpt-5.jpeg
   rm deploy-docker.sh
   rm kill-docker.sh
   rm run-docker.sh

   git add --all
   git status
   ```

   If there is no other relevant stuff in `docs/maintainers/` folder, then delete it altogether:
   ```bash
   rm -rf docs/maintainers/

   git add --all
   git status
   ```

   Commit and push:
   ```bash
   git commit -m "Delete irrelevant files"
   git push
   git status
   ```

TODO Advice to check `docs/DOCKER_PUBLISHING.md` against similar section(s) in `README_BOILERPLATE.md` first

TODO Advice to review all these files before the actual deletion

### Swap README

5. Override `README.md` with `README_BOILERPLATE.md`:
   ```bash
   git switch boilerplate-MANUAL-merging-branch
   git pull
   git status
   ```
   ```bash
   mv README_BOILERPLATE.md README.md

   git add --all
   git status
   ```
   ```bash
   git commit -m "Override README with README_BOILERPLATE.md"
   git push
   git status
   ```
6. Restore the following note at the top of the new README (replace the existing **ATTENTION** clause with it):
   ```markdown
   > **NOTE:** If you want to go back to the `Claude Code CLI Proxy` version of this repository, click [here](https://github.com/teremterem/claude-code-gpt-5).
   ```
   ---

   ```bash
   git add --all
   git status
   ```
   ```bash
   git commit -m "Restore note about going back to CLI Proxy version"
   git push
   git status
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
21. [NOTE: PROBABLY SHOULD NOT BE DONE, BECAUSE `X.X.X-bpX` VERSION FORMAT IS NOT SUPPORTED IN `pyproject.toml`] Update version too `X.X.X.X` (last component for the version of the boilerplate itself within the global claude code proxy release)
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
29. Publish TWO new images to GitHub Container Registry (TODO Provide a command to do this):
    - `ghcr.io/teremterem/litellm-server-yoda:X.X.X.X`
    - `ghcr.io/teremterem/litellm-server-yoda:X.X.X`
    - `ghcr.io/teremterem/litellm-server-yoda:latest`
    - `ghcr.io/teremterem/librechat-yoda:X.X.X.X`
    - `ghcr.io/teremterem/librechat-yoda:X.X.X`
    - `ghcr.io/teremterem/librechat-yoda:latest`
