# Devcontainer Dockerfile: Node 20 + website development tools
FROM mcr.microsoft.com/devcontainers/javascript-node:0-20

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    unzip \
    zip \
    openssh-client \
    apt-transport-https \
    sudo \
    ripgrep \
    jq \
    tree \
    shellcheck \
    imagemagick \
    sqlite3 \
    less \
    nano \
    vim \
    git-lfs \
  && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
  && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
  && apt-get update \
  && apt-get install -y gh \
  && rm -rf /var/lib/apt/lists/*

# Give the default non-root user passwordless sudo (convenience)
RUN if id -u node >/dev/null 2>&1; then usermod -aG sudo node; echo 'node ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/99_node-nopasswd; fi

USER node

# Install pixi for Python environment management and RenderCV tasks
RUN curl -fsSL https://pixi.sh/install.sh | bash
ENV PATH="/home/node/.pixi/bin:${PATH}"
