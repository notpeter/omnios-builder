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
`Experimental arm64` workflow provides an isolated hosted build and produces
short-lived workflow artifacts. `Publish experimental arm64` accepts a successful
build run ID and publishes its image as the separate `v2.1.4-aarch64.1` prerelease,
without changing the latest stable release or the default branch. It uses the
repository's `GITHUB_TOKEN` so release events do not start the general x86 build
or README-update workflows.

The image follows the existing builder's public test-key contract: the
`-host.id_rsa` sidecar is generated on the disposable build runner and grants
root access to this CI image. It is deliberately distributed with the image;
do not treat it as a secret credential or use this image as a production host.

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
- Installed `rsync` and `build-essential` from the arm64 repository; GCC 14.3.0
  compiled and ran the native C smoke test. The output was an ELF64 aarch64
  executable. SCP, rsync and tar round trips passed, including symlinks, executable
  permissions and filenames with spaces.
- Full isolated local image build completed successfully, including provisioning,
  restart, package installation, shutdown and export. `qemu-img check` reported
  zero errors and `zstd --test` passed for the exported artifact.
- The [first hosted image build](https://github.com/notpeter/omnios-builder/actions/runs/43635960060)
  passed. Its image also booted with the patched runtime locally; SSH, rsync in
  both directions and clean shutdown passed.
- The [final hosted rebuild](https://github.com/notpeter/omnios-builder/actions/runs/43638634261)
  and [published-image action validation](https://github.com/notpeter/omnios-vm/actions/runs/43641173749)
  passed. The action compiled and ran native C, forwarded environment variables,
  synchronized files in both directions, and exercised its persistent shell
  wrapper on both `ubuntu-24.04` (QEMU 8.2.2) and `ubuntu-26.04-arm` (QEMU 10.2.1).
  The separate r151060 x86 regression test also passed.
- [Prerelease publication](https://github.com/notpeter/omnios-builder/actions/runs/43640645287)
  passed. Every published checksum matched the final build artifact. The
  published image and firmware also passed a fresh local runtime download,
  boot, SSH, DNS, bidirectional rsync and clean shutdown.
