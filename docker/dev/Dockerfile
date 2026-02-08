ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_DIR=/tmp/build
ARG UBUNTU=24.04
FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-${UBUNTU} AS dev
SHELL ["/bin/bash", "-c"]

USER root
# Install dev dependencies.
RUN DEBIAN_FRONTEND=noninteractive && \
    apt-get update -y && \
    apt-get install -y curl \
    build-essential \
    pkg-config \
    libssl-dev \
    libsqlite3-dev \
    libbz2-dev \
    libreadline-dev \
    libffi-dev \
    liblzma-dev \
    gdal-bin \
    cmake \
    git \
    jq \
    vim \
    iputils-ping \
    docker.io \
    postgresql-client

# Install just.
USER vscode
RUN mkdir -p /home/vscode/bin
ENV PATH="/home/vscode/bin:$PATH"
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | \
    bash -s -- --to ~/bin

USER root
RUN groupadd -g 1001 docker-dev || true
RUN usermod -aG docker-dev vscode

# Update .bashrc to auto-export environment variables.
USER vscode
RUN echo -e '\n# Automatically export environment variables.\nset -a' >> /home/vscode/.bashrc

# Install git-lfs.
USER root
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get update -y && \
    apt-get install -y apt-transport-https ca-certificates && \
    apt-get update -y && \
    apt-get install -y git-lfs

# Install GitHub CLI.
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update -y && \
    apt-get install -y gh

# Install pyenv and Python.
ARG PYTHON
WORKDIR /home/vscode
ENV PATH="/home/vscode/.pyenv/bin:/home/vscode/.pyenv/shims:${PATH}"
USER vscode
RUN curl https://pyenv.run | bash && \
    export PATH="/home/vscode/.pyenv/bin:/home/vscode/.pyenv/shims:${PATH}" && \
    eval "$(pyenv init -)" && \
    pyenv install ${PYTHON} && \
    pyenv global ${PYTHON} && \
    python --version && which python && pip --version && which pip
RUN echo -e '\nexport PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$PATH"\neval "$(pyenv init -)"' >> /home/vscode/.bashrc
RUN export PATH="/home/vscode/.pyenv/bin:/home/vscode/.pyenv/shims:${PATH}" && \
    eval "$(pyenv init -)" && \
    pip install --upgrade pip && \
    pip install uv

# Add SSH agent function to .bashrc.
RUN tee -a /home/vscode/.bashrc > /dev/null <<'EOF'

# SSH agent function.
ssh-start() {
    if [ -z "$SSH_AUTH_SOCK" ] || ! ssh-add -l >/dev/null 2>&1; then
        echo "Starting SSH agent..."
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_ed25519
        echo "SSH agent started and key added."
    else
        echo "SSH agent already running with keys loaded"
        ssh-add -l
    fi
}
EOF

# Install Claude Code.
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash

# Clean up.
USER root
RUN rm -rf ${BUILD_DIR} && \
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy the entrypoint script.
COPY entrypoint.sh /entrypoint
RUN chmod +x /entrypoint
USER vscode
RUN git lfs install
ENTRYPOINT ["/bin/bash", "/entrypoint"]
