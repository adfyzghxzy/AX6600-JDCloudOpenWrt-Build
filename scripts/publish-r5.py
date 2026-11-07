#!/usr/bin/env python3
"""Publish the already-built Test5 images as R5; never compile firmware."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

REPO = "adfyzghxzy/AX6600-JDCloudOpenWrt-Build"
RUN = 42321445516
SOURCE = "0ecd22c785da58faa1444502ba441fb66a1fe690"
TAG = "v25.12.6-jdcloud-r5"
ARTIFACTS = {
    "standard": (13555911583, "sha256:90b21b047c95b8189e0c016e838e26bd20130b538a6296d3be41f9a4adf6c240"),
    "nss": (13555180581, "sha256:e993254523ec9beecb719ea7a497d8fde1082f479e1e9a620ebd6c98d7ad627d"),
}

def gh(*args, payload=None):
    result = subprocess.run(["gh", *args], input=payload, text=True,
                            capture_output=True, check=True)
    return result.stdout

def api(path, method="GET", data=None):
    args = ["api", f"repos/{REPO}/{path}", "--method", method]
    if data is not None:
        args += ["--input", "-"]
    return json.loads(gh(*args, payload=json.dumps(data) if data is not None else None))

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def verify_source():
    run = api(f"actions/runs/{RUN}")
    assert run["conclusion"] == "success" and run["head_sha"] == SOURCE
    artifacts = api(f"actions/runs/{RUN}/artifacts")["artifacts"]
    for variant, (artifact_id, checksum) in ARTIFACTS.items():
        artifact = next(a for a in artifacts if a["id"] == artifact_id)
        assert not artifact["expired"]
        assert artifact["name"] == f"re-cs-02-openwrt-25.12.6-{variant}-test5"
        assert artifact["digest"] == checksum
    return artifacts

def prepare():
    artifacts = verify_source()
    out = Path("release-assets")
    out.mkdir(exist_ok=True)
    mapping = []
    for variant, (artifact_id, _) in ARTIFACTS.items():
        source = Path("downloaded") / variant
        lines = (source / "SHA256SUMS").read_text().splitlines()
        expected = {}
        for line in lines:
            checksum, name = line.split(maxsplit=1)
            name = name.lstrip("*")
            assert Path(name).name == name
            expected[name] = checksum
        names = {f"openwrt-25.12.6-jdcloud-re-cs-02-{variant}-test5-{kind}.bin"
                 for kind in ("sysupgrade", "factory")}
        assert set(expected) == names
        for oldname in sorted(names):
            old = source / oldname
            assert digest(old) == expected[oldname], oldname
            newname = oldname.replace("-test5-", "-r5-")
            dest = out / newname
            shutil.copyfile(old, dest)
            assert digest(dest) == expected[oldname]
            mapping.append({"variant": variant, "artifact_id": artifact_id,
                            "original_name": oldname, "release_name": newname,
                            "sha256": digest(dest)})
        sysupgrade = source / f"openwrt-25.12.6-jdcloud-re-cs-02-{variant}-test5-sysupgrade.bin"
        factory = source / f"openwrt-25.12.6-jdcloud-re-cs-02-{variant}-test5-factory.bin"
        subprocess.run(["python3", "scripts/check-sysupgrade.py", str(sysupgrade)], check=True)
        subprocess.run(["python3", "scripts/check-factory.py", str(sysupgrade), str(factory)], check=True)
        with zipfile.ZipFile(out / f"build-info-{variant}-r5.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source.rglob("*")):
                if path.is_file() and path.suffix != ".bin":
                    info = zipfile.ZipInfo(str(path.relative_to(source)), (2026, 11, 7, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, path.read_bytes())
    (out / "SOURCE.json").write_text(json.dumps({
        "source_run": RUN, "source_commit": SOURCE, "recompiled": False,
        "artifacts": [{"id": a["id"], "name": a["name"], "digest": a["digest"]}
                      for a in artifacts if a["id"] in {v[0] for v in ARTIFACTS.values()}],
        "firmware": mapping}, ensure_ascii=False, indent=2) + "\n")
    paths = sorted(p for p in out.iterdir() if p.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(f"{digest(p)}  {p.name}\n" for p in paths))
    return sorted(out.iterdir())

def publish(paths):
    releases = api("releases?per_page=100")
    matches = [r for r in releases if r["tag_name"] == TAG]
    release = matches[0] if matches else api("releases", "POST", {
        "tag_name": TAG, "target_commitish": SOURCE,
        "name": "JDCloud AX6600 — OpenWrt 25.12.6 R5 (Standard + NSS)",
        "body": Path("docs/releases/r5.md").read_text(),
        "draft": True, "prerelease": True})
    existing = {a["name"]: a for a in api(f"releases/{release['id']}/assets")}
    for path in paths:
        if path.name in existing:
            assert existing[path.name].get("digest") == "sha256:" + digest(path), path.name
        else:
            gh("release", "upload", TAG, str(path), "--repo", REPO)
    assets = api(f"releases/{release['id']}/assets")
    byname = {a["name"]: a for a in assets}
    for path in paths:
        assert byname[path.name]["size"] == path.stat().st_size
        assert byname[path.name].get("digest") == "sha256:" + digest(path)
    # Preserve R1 firmware/tag; only clarify its description.
    gh("release", "edit", "v25.12.6-jdcloud-r1", "--repo", REPO,
       "--title", "JDCloud AX6600 — OpenWrt 25.12.6 R1 (Standard nền)",
       "--notes-file", "docs/releases/r1.md")
    result = api(f"releases/{release['id']}", "PATCH", {
        "body": Path("docs/releases/r5.md").read_text(),
        "draft": False, "prerelease": True})
    print(result["html_url"])

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--verify-source"]:
        verify_source()
    else:
        publish(prepare())
