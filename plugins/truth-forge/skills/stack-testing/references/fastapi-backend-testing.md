> Incorporated from the `python-fastapi-backend-testing` skill (skills-ref.zip).

# Python FastAPI Claude Backend Testing

## APPLICABILITY GUARD

This skill is specific to **claude-code-api** Python FastAPI backends exposing OpenAI-compatible HTTP/SSE API. Adapt paths, ports, and schemas before applying to other FastAPI projects.

## When to Use

- Testing claude-code-api Python backend
- Writing curl commands for chat completions
- Debugging SSE streaming issues
- Verifying Claude CLI integration

## When NOT to Use

- Testing non-claude-code-api FastAPI projects (adapt first)
- Frontend testing (use `webapp-testing` or `e2e-testing`)
- General Python testing (use `python-testing`)

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Use single-quote JSON with special chars in curl | JSON parse errors from unescaped characters | Use `printf '%s'` or heredoc `@-` for complex JSON |
| Omit `-N` flag for SSE streaming | curl buffers output, SSE events arrive in batches not real-time | Always `curl -N` for streaming requests |
| Skip `Accept: text/event-stream` header | Server may not negotiate SSE properly | Include header for all streaming requests |
| Set short timeout for Claude CLI responses | Claude CLI takes 10-30s; premature timeout = false failure | Use `--max-time 60` minimum |
| Declare PASS without verifying all response fields | Partial success hides broken fields | Check content, usage, session_id, finish_reason |


## Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| Default port | 8001 | 8000 used by Docker |
| Backend URL | `http://localhost:8001` | Configurable |
| Test project dir | `/tmp/claude-test-$$` | Use PID for isolation |

## Architecture

```
HTTP Client → FastAPI → subprocess.exec → Claude CLI → Claude API
```

## Core Test Patterns

### Health Check
```bash
curl -f http://localhost:8001/health
# Expect: {"status":"healthy","claude_version":"..."}
```

### Non-Streaming Chat
```bash
REQUEST_JSON=$(printf '%s' '{"model":"claude-3-5-haiku-20241022","messages":[{"role":"user","content":"Say: SUCCESS"}],"stream":false}')
curl -s --max-time 60 -X POST http://localhost:8001/v1/chat/completions \
  -H 'Content-Type: application/json' -d "$REQUEST_JSON" | jq '.choices[0].message.content'
```

### SSE Streaming
```bash
curl -s -N -X POST http://localhost:8001/v1/chat/completions \
  -H 'Content-Type: application/json' -H 'Accept: text/event-stream' \
  -d '{"model":"claude-3-5-haiku-20241022","messages":[{"role":"user","content":"Count to 3"}],"stream":true}'
```

### Tool Execution (File Creation)
```bash
TEST_FILE="/tmp/test-project/tool-test.txt"
timeout 40 curl -s -N -X POST http://localhost:8001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "{\"model\":\"claude-3-5-haiku-20241022\",\"messages\":[{\"role\":\"user\",\"content\":\"Create file at $TEST_FILE with text: Tool works\"}],\"stream\":true}" > /dev/null 2>&1
sleep 5 && [ -f "$TEST_FILE" ] && echo "PASS" || echo "FAIL"
```

## SSE Format Rules

- Each line: `data: {JSON}\n\n`
- First chunk: `delta.role` = "assistant"
- Content chunks: `delta.content` with text
- Final chunk: empty `delta`, `finish_reason` = "stop"
- Completion: `data: [DONE]\n\n`

## SSE Parsing

```bash
# Extract content from SSE stream
grep "^data: " stream.txt | grep -v "\[DONE\]" | sed 's/^data: //' | jq -r '.choices[0].delta.content // empty' | tr -d '\n'
# Verify format
grep -c "^data: " stream.txt  # >= 3
tail -1 stream.txt | grep "\[DONE\]"  # must match
```

## Verification Checklist

- [ ] Response is valid JSON (or valid SSE)
- [ ] All expected fields present
- [ ] Content is meaningful (not empty, not error)
- [ ] For tools: file exists with correct content
- [ ] For sessions: can continue with session_id
- [ ] Response time < 60s
