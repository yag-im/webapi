#!/usr/bin/env bash

mkdir -p /workspaces/webapi/.vscode
cp /workspaces/webapi/.devcontainer/vscode/* /workspaces/webapi/.vscode

make bootstrap
