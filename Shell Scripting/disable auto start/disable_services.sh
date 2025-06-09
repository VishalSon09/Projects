#!/bin/bash

# List of services to disable & stop
services=(
  # avahi-daemon.service
  # bluetooth.service
  cloud-config.service
  cloud-final.service
  cloud-init-local.service
  cloud-init.service
  cups.service
  cups-browsed.service
  # ModemManager.service
  openvpn.service
  # power-profiles-daemon.service
  # smartmontools.service
  # snapd.apparmor.service
  # snapd.autoimport.service
  # snapd.core-fixup.service
  # snapd.recovery-chooser-trigger.service
  # snapd.seeded.service
  # snapd.service
  # thermald.service
  # ufw.service
  # unattended-upgrades.service
  # wpa_supplicant.service
)

# Snap mounts to disable
snap_mounts=(
  snap-blender-6179.mount
  snap-blender-6181.mount
  snap-firefox-6159.mount
  snap-firefox-6198.mount
  snap-obsidian-45.mount
  snap-obsidian-47.mount
  snap-telegram\x2ddesktop-6597.mount
  snap-telegram\x2ddesktop-6639.mount
  snap-thunderbird-734.mount
  snap-thunderbird-735.mount
  snap-vlc-3777.mount
)

echo "Disabling and stopping services..."

for svc in "${services[@]}"; do
  echo "Disabling $svc"
  sudo systemctl disable "$svc"
  echo "Stopping $svc"
  sudo systemctl stop "$svc"
done

echo "Disabling snap mounts..."

for mount in "${snap_mounts[@]}"; do
  echo "Disabling $mount"
  sudo systemctl disable "$mount"
done


echo "Done! Please reboot your system for all changes to take full effect."
