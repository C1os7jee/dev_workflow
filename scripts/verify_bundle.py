"""Verify the vendored Matt Pocock skills without modifying files or using a network."""

import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


REPOSITORY = "https://github.com/mattpocock/skills"
COMMIT = "4ae2317ddb22b046e26455e4f9c9b3aaaf62212d"
SKILLS = frozenset({
    "setup-matt-pocock-skills", "grill-with-docs", "grilling", "domain-modeling",
    "codebase-design", "tdd", "diagnosing-bugs", "code-review", "to-spec",
    "to-tickets", "implement", "implement-spec",
})
ENTRY_DOCUMENTS = (
    "SKILL.md", "references/small.md", "references/large.md",
    "references/integration.md",
)
EXTERNAL_SKILLS = re.compile(
    r"\.(?:codex|claude|agents|cursor|gemini)[\\/]skills\b"
    r"|(?:~|[A-Za-z]:|\$(?:\{[A-Za-z_]\w*\}|[A-Za-z_]\w*)"
    r"|%[A-Za-z_]\w*%|(?<![\w:/])(?=/(?!/)))"
    r"[\\/](?:[^\s<>\"'`\[\]()]*(?:[\\/]))?skills(?:[\\/]|\b)",
    re.IGNORECASE,
)


class VerificationError(ValueError):
    """A bundle violates its manifest or the pinned source contract."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def relative_path(value, label):
    require(isinstance(value, str) and bool(value), f"{label}: expected a path")
    path = PurePosixPath(value)
    require(
        bool(path.parts) and not path.is_absolute() and path.as_posix() == value
        and all(part not in (".", "..") for part in path.parts)
        and not any(char in value for char in ("\\", ":", "\x00")),
        f"{label}: expected a normalized relative POSIX path: {value!r}",
    )
    return path


def walk_files(directory):
    # scandir propagates I/O failures and lets us reject links before traversal.
    with os.scandir(directory) as entries:
        for entry in entries:
            path = Path(entry.path)
            require(not entry.is_symlink(), f"symlink is not allowed: {path}")
            if entry.is_dir(follow_symlinks=False):
                yield from walk_files(path)
            else:
                require(entry.is_file(follow_symlinks=False), f"not a regular file: {path}")
                yield path


def difference(label, actual, expected):
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    details = []
    if missing:
        details.append("missing: " + ", ".join(map(str, missing)))
    if extra:
        details.append("extra: " + ", ".join(map(str, extra)))
    require(not details, f"{label}: {'; '.join(details)}")


def load_manifest(bundle):
    manifest = json.loads((bundle / "sources.json").read_text(encoding="utf-8"))
    require(isinstance(manifest, dict), "manifest: expected an object")
    require(manifest.get("repository") == REPOSITORY, "manifest: wrong repository")
    require(manifest.get("commit") == COMMIT, f"manifest: commit must be {COMMIT}")
    skills = manifest.get("skills")
    require(isinstance(skills, list) and len(skills) == 12, "manifest: expected 12 skills")
    directories = {}
    for skill in skills:
        require(isinstance(skill, dict), "manifest.skills: expected objects")
        name = skill.get("name")
        require(isinstance(name, str) and name in SKILLS, f"unknown skill: {name!r}")
        require(name not in directories, f"duplicate skill: {name}")
        directory = relative_path(skill.get("source_directory"), f"{name}.source_directory")
        category = "productivity" if name == "grilling" else "engineering"
        expected_directory = f"skills/{category}/{name}"
        require(directory.as_posix() == expected_directory,
                f"{name}: source_directory must be {expected_directory}")
        directories[name] = directory.as_posix()

    files = manifest.get("files")
    require(isinstance(files, list) and bool(files), "manifest.files: expected a nonempty list")
    paths = set()
    source_paths = set()
    for item in files:
        require(isinstance(item, dict), "manifest.files: expected objects")
        path = relative_path(item.get("path"), "file.path").as_posix()
        source = relative_path(item.get("source_path"), f"{path}.source_path").as_posix()
        require(path != "sources.json", "sources.json must not list itself")
        require(path.casefold() not in paths, f"duplicate bundled path: {path}")
        require(source not in source_paths, f"duplicate source path: {source}")
        paths.add(path.casefold())
        source_paths.add(source)
        for field in ("source_sha256", "bundled_sha256"):
            value = item.get(field)
            require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value),
                    f"{path}.{field}: expected a lowercase SHA-256 digest")
        changes = item.get("changes")
        require(isinstance(changes, list), f"{path}.changes: expected a list")
        renames = 0
        for change in changes:
            require(isinstance(change, dict), f"{path}: expected change objects")
            kind = change.get("kind")
            if kind == "rename-entry":
                require(set(change) == {"kind", "from", "to"}
                        and change["from"] == "SKILL.md" and change["to"] == "instructions.md",
                        f"{path}: invalid rename-entry rule")
                renames += 1
            elif kind == "replace-link":
                require(set(change) == {"kind", "from", "to", "count"},
                        f"{path}: invalid replace-link fields")
                for field in ("from", "to"):
                    require(isinstance(change[field], str) and bool(change[field])
                            and not any(char in change[field] for char in "\r\n\x00()"),
                            f"{path}: invalid replace-link {field}")
                require(type(change["count"]) is int and change["count"] > 0,
                        f"{path}: replace-link count must be a positive integer")
                require(change["from"] != change["to"], f"{path}: replace-link must change its target")
            else:
                raise VerificationError(f"{path}: unknown change kind: {kind!r}")
        require(any(change["kind"] == "replace-link" for change in changes)
                or item["source_sha256"] == item["bundled_sha256"],
                f"{path}: source_sha256 and bundled_sha256 must match without replace-link")
        require(renames <= 1, f"{path}: duplicate rename-entry rule")
        if renames:
            require(any(source == directory + "/SKILL.md" and path == name + "/instructions.md"
                        for name, directory in directories.items()),
                    f"{path}: rename-entry does not match the source and bundled paths")
        for name, directory in directories.items():
            if source.startswith(directory + "/"):
                source_relative = source[len(directory) + 1:]
                expected = "instructions.md" if source_relative == "SKILL.md" else source_relative
                require(path == name + "/" + expected, f"{path}: inconsistent source-to-bundle path")
                require(renames == (source_relative == "SKILL.md"),
                        f"{path}: entry rename must be registered exactly once")
                break
        else:
            raise VerificationError(f"{path}: source_path is outside declared skill directories: {source}")
    for name, directory in directories.items():
        require(any(item["source_path"] == directory + "/SKILL.md"
                    and item["path"] == name + "/instructions.md" for item in files),
                f"{name}: missing instructions.md entry")
    return directories, files


def verify_files(root, bundle, files):
    all_files = set(walk_files(root))
    difference("SKILL.md entries", {path.relative_to(root).as_posix() for path in all_files
                                    if path.name.casefold() == "skill.md"}, {"SKILL.md"})
    difference("bundled skill directories", {path.name for path in bundle.iterdir() if path.is_dir()}, SKILLS)
    actual = {path.relative_to(bundle).as_posix() for path in all_files
              if path.is_relative_to(bundle) and path != bundle / "sources.json"}
    difference("bundled files", actual, {item["path"] for item in files})
    for item in files:
        path = bundle / item["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["bundled_sha256"],
                f"bundled SHA-256 mismatch: {item['path']}")


def prose_without_code(text):
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines.append("\n")
        elif marker:
            fence = marker[1]
            lines.append("\n")
        elif line.startswith(("    ", "\t")):
            lines.append("\n")
        else:
            lines.append(line)
    text = re.sub(r"<!--[\s\S]*?-->", "", "".join(lines))
    return re.sub(r"(`+)[\s\S]*?(?<!`)\1(?!`)", "", text)


def markdown_targets(text):
    # Only the four authored entry documents are parsed; upstream templates are data.
    for match in re.finditer(r"(?<!\\)\]\(\s*", text):
        start = match.end()
        if start == len(text):
            continue
        if text[start] == "<":
            end = text.find(">", start + 1)
            if end != -1:
                yield text[start + 1:end]
            continue
        depth = 0
        end = start
        while end < len(text):
            char = text[end]
            if char == "\\":
                end += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace():
                break
            end += 1
        if end > start and end < len(text):
            yield text[start:end]
    for match in re.finditer(r"^ {0,3}\[[^\]\n]+\]:[ \t]*(<[^>\n]+>|\S+)", text, re.MULTILINE):
        yield match[1].strip("<>")


def verify_links(root, bundle):
    referenced = set()
    for relative in ENTRY_DOCUMENTS:
        document = root / relative
        text = document.read_text(encoding="utf-8")
        local_text = re.sub(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s<>\"'`]+", "", text)
        require(not EXTERNAL_SKILLS.search(local_text),
                f"{relative}: external local skills path dependency")
        for target in markdown_targets(prose_without_code(text)):
            target = html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", target))
            if target.startswith("#"):
                continue
            require(not re.match(r"^[A-Za-z]:[\\/]|^\\\\", target),
                    f"{relative}: absolute local link: {target}")
            parsed = urlsplit(target)
            require(parsed.scheme.lower() != "file", f"{relative}: local file URL: {target}")
            if parsed.scheme or parsed.netloc:
                continue
            decoded = unquote(parsed.path)
            if not decoded:
                continue
            require(not Path(decoded).is_absolute() and not re.match(r"^[A-Za-z]:", decoded)
                    and "\\" not in decoded, f"{relative}: invalid local link: {target}")
            resolved = (document.parent / decoded).resolve()
            require(resolved.is_relative_to(root), f"{relative}: link leaves the skill root: {target}")
            require(resolved.is_file(), f"{relative}: missing local file: {target}")
            referenced.add(resolved)
    instructions = {bundle / name / "instructions.md" for name in SKILLS}
    difference("unreferenced instructions.md", referenced & instructions, instructions)


def git_bytes(upstream, *arguments):
    environment = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(
        ["git", "--no-replace-objects", "-c", "protocol.allow=never", "-C", str(upstream), *arguments],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise VerificationError(f"git {arguments[0]} failed: {detail[0][:300] if detail else result.returncode}")
    return result.stdout


def verify_upstream(upstream, bundle, directories, files):
    require(upstream.is_dir(), f"upstream directory does not exist: {upstream}")
    git_bytes(upstream, "cat-file", "-e", COMMIT + "^{commit}")
    tree = git_bytes(upstream, "ls-tree", "-r", "-z", "--full-tree", COMMIT, "--",
                     *(directory + "/" for directory in directories.values()))
    actual = set()
    for record in tree.split(b"\x00"):
        if not record:
            continue
        metadata, path_bytes = record.split(b"\t", 1)
        mode, kind, _ = metadata.split(b" ")
        source = path_bytes.decode("utf-8")
        require(kind == b"blob" and mode in (b"100644", b"100755"),
                f"upstream is not a regular file: {source}")
        actual.add(source)
    expected = {item["source_path"] for item in files}
    difference("upstream directory files", actual, expected)
    for item in files:
        source = item["source_path"]
        original = git_bytes(upstream, "show", "--no-ext-diff", "--no-textconv", COMMIT + ":" + source)
        require(hashlib.sha256(original).hexdigest() == item["source_sha256"],
                f"source SHA-256 mismatch: {source}")
        rebuilt = original
        for change in item["changes"]:
            if change["kind"] == "replace-link":
                old = ("](" + change["from"] + ")").encode("utf-8")
                new = ("](" + change["to"] + ")").encode("utf-8")
                require(rebuilt.count(old) == change["count"],
                        f"{source}: replace-link count mismatch for {change['from']!r}")
                rebuilt = rebuilt.replace(old, new)
        require(rebuilt == (bundle / item["path"]).read_bytes(),
                f"rebuilt bytes differ: {item['path']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, metavar="PATH",
                        help="also verify source bytes at the pinned commit in a local Git repository (offline)")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    bundle = root / "references" / "matt-pocock"
    try:
        require(not bundle.is_symlink(), f"bundle must not be a symlink: {bundle}")
        directories, files = load_manifest(bundle)
        verify_files(root, bundle, files)
        verify_links(root, bundle)
        if args.upstream is not None:
            verify_upstream(args.upstream.resolve(), bundle, directories, files)
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    suffix = f"; upstream {COMMIT} verified" if args.upstream is not None else ""
    print(f"OK: 12 skills, {len(files)} bundled files, entry links verified{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
