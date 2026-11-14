# Experimental OmniOS arm64

The arm64 image starts from the official **braich r151059** snapshot, dated
2026-05-07. This is an experimental distribution based on
[arm64-gate](https://github.com/richlowe/arm64-gate), not a supported stable or
LTS release. Its package publishers are rolling `bloody/braich` repositories;
installing packages later can select newer userland versions than the snapshot.

Inputs are SHA256-pinned in `conf/omnios-r151059-aarch64.conf` and
`hooks/host_beforeBuild.py`. The upstream files and boot instructions are at
<https://downloads.omnios.org/media/braich/>. A changed upstream file fails the
build until its new contents have been reviewed and the pin updated.

Build on a disposable Ubuntu runner:

```sh
python3 build.py conf/omnios-r151059-aarch64.conf
```

Like the existing x86 builder, this command installs host packages and prepares
SSH configuration. Do not run it directly on a shared development host. The
`Experimental arm64` workflow provides an isolated hosted build. It publishes
short-lived workflow artifacts, not a stable release.

Boot requirements:

- QEMU `virt`, Cortex-A53, TCG, two CPUs and 3072 MB RAM.
- The upstream U-Boot binary; EDK2 is not used.
- `virtio-net-device` before `virtio-blk-device` (MMIO transport).
- A generated FDT with `/aliases/serial0` pointing to `/pl011@9000000`.
  QEMU 8.2 omits this alias; without it the loader cannot discover its UART and
  the kernel console goes silent. Generate the FDT for the actual CPU count,
  memory and devices rather than reusing a static tree across configurations.
- A serial console; no framebuffer, PCI RNG, or semihosting is needed.

First boot is slow under emulation, especially initial SMF setup. The builder
allows 30 minutes to reach login. The snapshot uses an empty root password,
requires DHCP setup on `vioif0`, and initially has files-only hostname lookup.
The provisioning hooks enable SSH, DNS lookup, and the existing NIC-discovery
startup script before installing rsync.

The action requires the matching experimental runtime changes in
`notpeter/omnios-vm` on `illumos_aarch64`; stock anyvm 0.7.7 assumes an EDK2/PCI
arm64 guest and cannot launch this image correctly.

## Validation record

- Local QEMU 8.2.2: boot, ZFS root mount, two online CPUs, root console login,
  DHCP, public-key SSH and DNS confirmed on 2026-11-14.
- `uname -a`: `SunOS braich 5.11 arm64-gate-0-g1ba5fbc24a armv8 aarch64 QEMU,virt`.
- Compared generated r151060 x86 QEMU arguments and profile with commit
  `eb504cd`: identical.
- Hosted image build and end-to-end action validation are in progress.
