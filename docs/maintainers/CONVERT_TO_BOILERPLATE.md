# Converting to Boilerplate (aka My LiteLLM Server)

This guide is intended for the maintainers of the Claude Code GPT-5 repository to derive a "Boilerplate" version of it (aka My LiteLLM Server) upon a new version release. **If you are simply looking to use it as a boilerplate, head over to the [main-boilerplate](https://github.com/teremterem/claude-code-gpt-5/tree/main-boilerplate) branch of this repository and check out the [README](https://github.com/teremterem/claude-code-gpt-5/blob/main-boilerplate/README.md) there.**

## Steps

> **NOTE:** All the commands below are expected to be run from the root directory of the repository:

```bash
cd <repo-root-dir>
```

### Preparation

1. Backup the content of the `main` branch of the repo to a separate directory:

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

2. Backup the content of the `main-boilerplate` branch of the repo to a separate directory:

   ```bash
   rm -ri ../repo-boilerplate-backup-dir
   ```

   > **NOTE:** The command above will ask about deleting each and every file. If the directory exists already, this will make you cognizant of this fact. **Retry without `-i` to actually delete it** (no confirmations will be asked).

   Proceed with the backup:

   ```bash
   git switch main-boilerplate
   git pull
   git status
   ```

   ```bash
   cp -r . ../repo-boilerplate-backup-dir
   rm -rf ../repo-boilerplate-backup-dir/.git
   rm -rf ../repo-boilerplate-backup-dir/.venv
   rm ../repo-boilerplate-backup-dir/.env
   rm ../repo-boilerplate-backup-dir/librechat/.env
   ```

3. Create a feature branch from `main-boilerplate`:

   > ⚠️ **ATTENTION** ⚠️ If `boilerplate-merging-branch` already exists, first make sure to delete it both - locally and from the remote.

   ```bash
   git switch --create boilerplate-merging-branch
   ```

   ```bash
   git push --set-upstream origin boilerplate-merging-branch
   ```

4. Merge `main` branch into this feature branch in the following way:

   2.1 Switch to the feature branch and **initiate the merge** of the `main`:

   ```bash
   git merge origin/main
   git status
   ```

   2.2 **IGNORE ALL THE MERGE CONFLICTS (if any).** Override everything with the files from the `main` branch and conclude the merge **(do this regardless of the presence or absence of merge conflicts):**

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

5. **Create a feature branch from the feature branch:**

   > ⚠️ **ATTENTION** ⚠️ If `boilerplate-MANUAL-merging-branch` already exists, first make sure to delete it both - locally and from the remote.

   ```bash
   git switch --create boilerplate-MANUAL-merging-branch
   ```

   ```bash
   git push --set-upstream origin boilerplate-MANUAL-merging-branch
   ```

### Delete irrelevant files

6. Delete the following files and folders, as they are not supposed to be part of the boilerplate:

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

### Swap the README

7. Override `README.md` with `README_BOILERPLATE.md`:

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

8. Edit the new `README.md` to restore a **NOTE** clause at the top of it:

   ```bash
   vim README.md
   ```

   **Replace the existing ATTENTION clause at the top with the following text:**

   ```markdown
   > **NOTE:** If you want to go back to the `Claude Code CLI Proxy` version of this repository, click [here](https://github.com/teremterem/claude-code-gpt-5).
   ```

   ```bash
   git add --all
   git status
   ```

   ```bash
   git commit -m "Restore note about going back to CLI Proxy version"
   git push
   git status
   ```

### Restore boilerplate-specific versions of certain files

9. Copy the following files over from the `main-boilerplate` branch:

   ```bash
   cp ../repo-boilerplate-backup-dir/docs/DOCKER_TIPS.md docs/
   cp ../repo-boilerplate-backup-dir/.env.template .
   cp ../repo-boilerplate-backup-dir/config.yml .
   cp ../repo-boilerplate-backup-dir/docker-compose.dev.yml .
   cp ../repo-boilerplate-backup-dir/docker-compose.yml .
   cp ../repo-boilerplate-backup-dir/uv-run.sh .

   git add --all
   git status
   ```

   TODO Advice to review both variants (the diff) to see if there is anything useful in the non-boilerplate version that might make sense to incorporate into the boilerplate version

   ```bash
   git commit -m "Restore boilerplate-specific versions of certain files"
   git push
   git status
   ```

### Correct certain files manually

10. REMOVE the following entries from `config.yaml`:

    ```bash
    vim config.yaml
    ```

    ```yaml
    # litellm_settings: custom_provider_map:
    - provider: claude_code_router
      custom_handler: claude_code_proxy.claude_code_router.claude_code_router
    ```

    ```yaml
    # model_list:
    - model_name: "*"
      litellm_params:
        model: "claude_code_router/*"
        drop_params: true  # Automatically drop unsupported parameters
    ```

11. REMOVE the following lines from `Dockerfile`:

    ```bash
    vim Dockerfile
    ```

    ```dockerfile
    LABEL org.opencontainers.image.source=https://github.com/teremterem/claude-code-gpt-5 \
          org.opencontainers.image.description="Connect Claude Code CLI to GPT-5" \
          org.opencontainers.image.licenses=MIT
    ```

12. Update the `name`, `version` and `description` fields in `pyproject.toml` in the following way:

    ```bash
    vim pyproject.toml
    ```

    ```toml
    # ...
    name = "my-litellm-server"
    version = "X.X.X.X"  # Replace with numbers
    description = "LiteLLM server boilerplate"
    # ...
    ```

    As you can see, the `version` number has four components. **The last component is the version of the boilerplate itself within the global claude code proxy release.**

13. Regenerate `uv.lock` file:

    ```bash
    uv lock --no-upgrade
    ```

    > **NOTE:** You are not meant to upgrade any packages with the `--upgrade` flag while converting to boilerplate - that is meant to be done earlier, as part of the `main` branch development.

14. Commit and push:

    ```bash
    git add --all
    git status
    ```

    ```bash
    git commit -m "Update pyproject.toml, Dockerfile and uv.lock"
    git push
    git status
    ```

### Merge the rest of the files the usual way

The remaining files and folders should be merged the usual way. Files and folders like:
- `common/`
- `librechat/`
- `yoda_example/`
- the rest of the files in the root directory
- etc.

So, in order to conclude the conversion, do the following:

15. Create a GitHub Pull Request of `boilerplate-MANUAL-merging-branch` into `boilerplate-merging-branch`:

    ```bash
    gh pr create \
       --base boilerplate-merging-branch \
       --head boilerplate-MANUAL-merging-branch \
       --title 'Merge '\`'boilerplate-MANUAL-merging-branch'\`' into '\`'boilerplate-merging-branch'\` \
       --body ""
    ```

    (Or do this through the GitHub web interface, if you prefer.)

16. **Thoroughly review the diff in this PR and make changes in `boilerplate-MANUAL-merging-branch` if needed.**

### Final steps

17. Take a moment to think if nothing was forgotten (e.g. something new was introduced, which this guide doesn't cover yet).

18. SQUASH and merge `boilerplate-MANUAL-merging-branch` into `boilerplate-merging-branch` using the Pull Request created in step 15:

    ```bash
    gh pr merge --squash --delete-branch --auto
    ```

19. **Thoroughly test `boilerplate-merging-branch`.**

20. Create a GitHub Pull Request of `boilerplate-merging-branch` into `main-boilerplate`:

    ```bash
    gh pr create \
       --base main-boilerplate \
       --head boilerplate-merging-branch \
       --title 'Merge '\`'boilerplate-merging-branch'\`' into '\`'main-boilerplate'\` \
       --body ""
    ```

    (Or do this through the GitHub web interface, if you prefer.)

21. Merge `boilerplate-merging-branch` into `main-boilerplate` using the Pull Request created in step 20. **DO NOT SQUASH, DO MERGE COMMIT INSTEAD!** We want `main-boilerplate` to be marked as in-sync with the `main` branch.

    ```bash
    gh pr merge --squash --delete-branch --auto
    ```

22. **Do a very shallow test of `main-boilerplate`.** (Proper testing was performed in step 19.)

23. Tag the new version:

    ```bash
    git tag -a X.X.X.X -m "Release X.X.X.X" # Replace with the actual version number
    git push --tags
    git status
    ```

24. Go to the GitHub Releases page and create a new release:
    - **Title:** `X.X.X.X (boilerplate release)`
    - **Description:** \<release notes\>
    - **Discussion:** create a new discussion
    - **Mark as latest:** FALSE

25. Login to GHCR:

    ```bash
    echo <YOUR_GITHUB_PAT> | docker login ghcr.io -u <YOUR_GITHUB_USERNAME> --password-stdin
    ```

26. Build the `litellm-server-yoda` image and push it to GHCR:

    ```bash
    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      -t ghcr.io/teremterem/litellm-server-yoda:<X.X.X.X> \
      -t ghcr.io/teremterem/litellm-server-yoda:<X.X.X> \
      -t ghcr.io/teremterem/litellm-server-yoda:latest \
      --push .
    ```

27. Build the `librechat-yoda` image and push it to GHCR:

    ```bash
    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      -t ghcr.io/teremterem/librechat-yoda:<X.X.X.X> \
      -t ghcr.io/teremterem/librechat-yoda:<X.X.X> \
      -t ghcr.io/teremterem/librechat-yoda:latest \
      --push .
    ```
