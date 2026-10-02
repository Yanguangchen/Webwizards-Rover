#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -eq 0 ]]; then
  echo 'Run this as the rover user, without sudo. It will request sudo where needed.' >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd -- "$script_dir/.." && pwd)"
unit_source="$skill_dir/assets/rover-stream-boot.service"

sudo install -m755 "$script_dir/rover-stream" /usr/local/bin/rover-stream
mkdir -p "$HOME/.config/systemd/user"
install -m644 "$unit_source" "$HOME/.config/systemd/user/rover-stream-boot.service"
sudo loginctl enable-linger "$(id -un)"
systemctl --user daemon-reload
systemd-analyze --user verify "$HOME/.config/systemd/user/rover-stream-boot.service"
systemctl --user enable --now rover-stream-boot.service

echo 'Installed rover-stream and enabled StampNote robotic-control at boot.'
