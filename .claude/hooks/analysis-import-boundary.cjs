#!/usr/bin/env node
/**
 * Analysis import-boundary guard.
 *
 * Hook type: PreToolUse (Write|Edit|MultiEdit)
 *
 * Enforces the project's core architectural invariant (see CLAUDE.md): the
 * `analysis/` engine must stay import-free of Django and pytest so it remains
 * unit-testable in isolation. Blocks edits that introduce `import django`,
 * `import pytest`, or `from django`/`from pytest` inside analysis/**\/*.py.
 *
 * @module analysis-import-boundary
 */

"use strict";

const FORBIDDEN = /^\s*(import\s+(django|pytest)\b|from\s+(django|pytest)\b)/m;

function readStdin() {
  try {
    return require("fs").readFileSync(0, "utf8");
  } catch {
    return "";
  }
}

function extractPathAndContent(input) {
  let data;
  try {
    data = JSON.parse(input);
  } catch {
    return null;
  }
  const toolInput = data.tool_input ?? data;
  const filePath = toolInput.file_path ?? "";
  const content =
    toolInput.content ?? toolInput.new_string ?? toolInput.new_str ?? "";
  return { filePath, content };
}

function main() {
  const parsed = extractPathAndContent(readStdin());
  if (!parsed) {
    return;
  }
  const { filePath, content } = parsed;
  if (!/\/analysis\/.*\.py$/.test(filePath.replace(/\\/g, "/"))) {
    return;
  }
  if (!FORBIDDEN.test(content)) {
    return;
  }
  console.log(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason:
          "analysis/ must stay import-free of Django and pytest (CLAUDE.md invariant) — this edit introduces a django/pytest import.",
      },
    })
  );
}

main();
