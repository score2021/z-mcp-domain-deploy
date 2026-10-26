#!/bin/sh
# Install only this skill. Existing directories and dangling symlinks are protected.
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target_dir="$HOME/.agents/skills/z-mcp-domain-deploy"
if [ -e "$target_dir" ] || [ -L "$target_dir" ]; then
    echo 'Skill target already exists; nothing overwritten.' >&2
    exit 1
fi
mkdir -p -- "$HOME/.agents/skills"
mkdir -- "$target_dir"
for item in SKILL.md domain-and-icp.md https-and-mcp.md sources.md Caddyfile.template render-caddy.py LICENSE; do
    cp -- "$source_dir/$item" "$target_dir/$item"
done
printf '%s\n' 'Installed z-mcp-domain-deploy. Open a new Codex session and invoke $z-mcp-domain-deploy.'
