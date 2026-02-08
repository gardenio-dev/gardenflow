# TODO

## Dev Container

- [ ] The Python version is hardcoded in
  `.devcontainer/docker-compose.yml` (`PYTHON=3.11.3`) rather than
  being read from `.python-version`. Docker Compose build args
  don't support reading from files directly. If `.python-version`
  changes, the compose file must be updated manually to match.
