# test-integrations: rc=1 under node was MY invocation error, not a repo defect

- tools/test-integrations.mjs:1  `#!/usr/bin/env bun`
- tools/test-integrations.mjs:20 `// Run: bun tools/test-integrations.mjs`
- tools/test-integrations.mjs:42 `resolve(import.meta.dir, "..")` — `import.meta.dir`
  is Bun-only; under Node it is `undefined` -> ERR_INVALID_ARG_TYPE paths[0].

Superseded record kept: test-integrations.WRONG-RUNTIME-node.{log,rc} (rc=1)
Correct record:          test-integrations-bun.{log,rc}                 (rc=0, 36 pass, 0 fail)
