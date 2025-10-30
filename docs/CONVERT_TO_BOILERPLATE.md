1. Create a feature branch from `main-boilerplate`
2. Merge `main` branch into this feature branch
3. Create a feature branch from this feature branch ?
4. Delete `claude_code_proxy` folder
5. Delete `docs/CONVERT_TO_BOILERPLATE.md`
6. Delete `docs/DOCKER_PUBLISHING.md`
   - TODO Advice to check against similar section(s) in `README_BOILERPLATE.md` first
7. Delete `images/claude-code-gpt-5.jpeg`
8. Delete `deploy-docker.sh`
9. Delete `kill-docker.sh`
10. Delete `run-docker.sh`
11. Override `README.md` with `README_BOILERPLATE.md`
12. Restore this note at the top of this new README:
    ```markdown
    > **NOTE:** If you want to go back to the `Claude Code CLI Proxy` version of this repository, click [here](https://github.com/teremterem/claude-code-gpt-5).
    ```
13. Restore `docs/DOCKER_TIPS.md` as it was in the `main-boilerplate` branch
    - TODO Advice to read both variants first, though - just to see if there is anything useful in the non-boilerplate version that might make sense to incorporate into the boilerplate version


---

100499. SQUASH and merge the feature of the feature branch into the feature branch
100500. Merge this feature branch into `main-boilerplate` (DO NOT SQUASH, JUST MERGE!)
