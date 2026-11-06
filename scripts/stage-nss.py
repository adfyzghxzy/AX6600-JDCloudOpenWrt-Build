#!/usr/bin/env python3
"""Add the pinned LiBwrt NSS hardware layer to the OpenWrt stable build tree."""
from pathlib import Path
import shutil
import sys

stable, libwrt, custom = map(Path, sys.argv[1:])
target = Path('target/linux/qualcommax')
# Preserve stable target defaults. NSS packages are selected explicitly in config.
stable_target = (stable / target / 'Makefile').read_text()
stable_subtarget = (stable / target / 'ipq60xx/target.mk').read_text()

for relative in [
    target,
    Path('package/kernel/mac80211'),
    Path('package/kernel/qca-nss-dp'),
    Path('package/kernel/qca-ssdk'),
    Path('package/firmware/ath11k-firmware'),
    Path('package/firmware/ipq-wifi'),
]:
    shutil.rmtree(stable / relative)
    shutil.copytree(libwrt / relative, stable / relative)

(stable / target / 'Makefile').write_text(stable_target)
(stable / target / 'ipq60xx/target.mk').write_text(stable_subtarget)
patch = Path('target/linux/generic/hack-6.12/952-net-conntrack-events-support-multiple-registrant.patch')
shutil.copy2(libwrt / patch, stable / patch)
kernel_config = stable / target / 'config-6.12'
kernel_config.write_text(kernel_config.read_text() + '\nCONFIG_NF_CONNTRACK_CHAIN_EVENTS=y\n')

# Retain the primary eMMC layout already qualified on this router.
image = stable / target / 'image/ipq60xx.mk'
text = image.read_text()
start = text.index('define Device/jdcloud_re-cs-02\n')
end = text.index('TARGET_DEVICES += jdcloud_re-cs-02', start)
text = text[:start] + """define Device/jdcloud_re-cs-02
	$(call Device/FitImage)
	$(call Device/EmmcImage)
	DEVICE_VENDOR := JDCloud
	DEVICE_MODEL := RE-CS-02
	SOC := ipq6010
	BLOCKSIZE := 64k
	KERNEL_SIZE := 6144k
	DEVICE_DTS_CONFIG := config@cp03-c3
	DEVICE_PACKAGES := ipq-wifi-jdcloud_re-cs-02 ath11k-firmware-qcn9074 kmod-ath11k-pci
	IMAGES := sysupgrade.bin factory.bin
	IMAGE/factory.bin := append-kernel | pad-to $$(KERNEL_SIZE) | append-rootfs | append-metadata
endef
""" + text[end:]
image.write_text(text)

dts = stable / target / 'files/arch/arm64/boot/dts/qcom/ipq6010-re-cs-02.dts'
dts.write_text(dts.read_text() + """
&{/chosen} {
	bootargs-append = " root=PARTLABEL=rootfs rootwait";
};
""")

files = stable / 'files'
files.mkdir(exist_ok=True)
shutil.copytree(custom / 'files', files, dirs_exist_ok=True)
shutil.copytree(custom / 'nss-files', files, dirs_exist_ok=True)
print('Staged LiBwrt NSS hardware layer on the pinned OpenWrt stable source')
