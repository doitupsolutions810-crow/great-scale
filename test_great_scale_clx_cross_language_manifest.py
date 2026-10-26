#!/usr/bin/env python3
"""CLX: audit JavaScript test entrypoints as well as Python modules."""
import json
from pathlib import Path
import re
import tempfile


NODE_TEST = re.compile(r"node\s+(test(?:[A-Za-z0-9_.-]*)\.(?:js|cjs|mjs))")


def audit_node_tests(root: Path, test_command: str):
    targets = []
    unsafe_segments = []
    for raw_segment in test_command.split("&&"):
        segment = raw_segment.strip()
        match = NODE_TEST.fullmatch(segment)
        if match:
            targets.append(match.group(1))
        else:
            unsafe_segments.append(segment)
    missing = sorted(path for path in targets if not (root / path).is_file())
    discovered = {
        path.name for path in root.iterdir()
        if path.is_file() and re.fullmatch(r"test.*\.(?:js|cjs|mjs)", path.name)
    }
    omitted = sorted(discovered - set(targets))
    return missing, omitted, unsafe_segments


def test_canonical_node_suite_covers_all_top_level_js_test_files():
    root = Path(__file__).resolve().parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    all_segments = [segment.strip() for segment in package["scripts"]["all"].split("&&")]
    assert "npm test" in all_segments, "npm run all must invoke npm test"
    missing, omitted, unsafe = audit_node_tests(root, package["scripts"]["test"])
    assert not unsafe, f"Unsupported Node test command segments: {unsafe}"
    assert not missing, f"Node test script references missing files: {missing}"
    assert not omitted, f"JavaScript test files omitted from npm test: {omitted}"


def test_audit_detects_an_omitted_javascript_test():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.js").write_text("// included\n", encoding="utf-8")
        (root / "test_beta.cjs").write_text("// omitted\n", encoding="utf-8")
        missing, omitted, unsafe = audit_node_tests(root, "node test_alpha.js")
        assert missing == []
        assert omitted == ["test_beta.cjs"]
        assert unsafe == []


def test_audit_rejects_success_fallback_that_masks_node_test_failure():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.js").write_text("// present\n", encoding="utf-8")
        missing, omitted, unsafe = audit_node_tests(
            root, "node test_alpha.js || true"
        )
        assert missing == []
        assert omitted == ["test_alpha.js"]
        assert unsafe == ["node test_alpha.js || true"]


if __name__ == "__main__":
    tests = [
        test_canonical_node_suite_covers_all_top_level_js_test_files,
        test_audit_detects_an_omitted_javascript_test,
        test_audit_rejects_success_fallback_that_masks_node_test_failure,
    ]
    for test in tests:
        test()
    print(f"PASS CLX cross-language test manifest audit ({len(tests)}/{len(tests)} tests)")
