<div align="center">

# MCP Server Starter

**TypeScript + OIDC npm Publishing + CI/CD.**

Build your MCP server. One-click publish. Zero secrets needed.

[![CI](https://github.com/starter-series/mcp-server-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/starter-series/mcp-server-starter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![npm version](https://img.shields.io/npm/v/my-mcp-server.svg)](https://www.npmjs.com/package/my-mcp-server)

**English** | [한국어](README.ko.md)

</div>

---

> **Part of [Starter Series](https://github.com/starter-series/starter-series)** — Stop explaining CI/CD to your AI every time. Clone and start.
>
> [Docker Deploy](https://github.com/starter-series/docker-deploy-starter) · [Discord Bot](https://github.com/starter-series/discord-bot-starter) · [Telegram Bot](https://github.com/starter-series/telegram-bot-starter) · [Browser Extension](https://github.com/starter-series/browser-extension-starter) · [Electron App](https://github.com/starter-series/electron-app-starter) · [npm Package](https://github.com/starter-series/npm-package-starter) · [React Native](https://github.com/starter-series/react-native-starter) · [VS Code Extension](https://github.com/starter-series/vscode-extension-starter) · **MCP Server**

---

## What You Get

- **MCP SDK** — `@modelcontextprotocol/sdk` with stdio transport
- **TypeScript** — Strict mode, ES2022 target, Zod-validated tool schemas
- **Safety Annotations** — readOnly/destructive/idempotent hints on every tool
- **Prompts** — Guided workflow templates for common tasks
- **Response Helpers** — `ok()` and `err()` for consistent tool responses
- **Config** — Environment variable parsing pattern
- **CI** — gitleaks, npm audit, license compliance, ESLint, build, test
- **CD** — OIDC trusted publishing to npm (zero secrets needed)
- **Dependabot** — Automated dependency + GitHub Actions updates

## Quick Start

```bash
git clone https://github.com/starter-series/mcp-server-starter.git my-mcp-server
cd my-mcp-server
rm -rf .git && git init

npm install
npm run dev
```

## Adding Tools

> **Tool names must be globally unique** across all MCP servers a client connects to. Prefix with your module name (e.g., `mymodule_action` instead of `action`).

Create `src/tools/your-tool.ts`:

```ts
import { z } from 'zod';
import { ok, err } from '../helpers.js';

export const name = 'your_tool';

export const config = {
  title: 'Your Tool',
  description: 'What your tool does',
  inputSchema: {
    input: z.string().describe('Input parameter'),
  },
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false,
  },
};

export async function handler({ input }: { input: string }) {
  try {
    return ok(`Processed: ${input}`);
  } catch (e) {
    return err(`Failed: ${e instanceof Error ? e.message : String(e)}`);
  }
}
```

Register in `src/index.ts`:

```ts
import * as yourTool from './tools/your-tool.js';
server.registerTool(yourTool.name, yourTool.config, yourTool.handler);
```

## Adding Prompts

Create `src/prompts/your-prompt.ts`:

```ts
import { z } from 'zod';

export const name = 'your-prompt';
export const description = 'Guided workflow description';

export const schema = {
  param: z.string().optional().describe('Optional parameter'),
};

export function handler({ param }: { param?: string }) {
  return {
    description,
    messages: [{
      role: 'user' as const,
      content: { type: 'text' as const, text: `Prompt text with ${param ?? 'default'}` },
    }],
  };
}
```

Register in `src/index.ts`:

```ts
import * as yourPrompt from './prompts/your-prompt.js';
server.prompt(yourPrompt.name, yourPrompt.description, yourPrompt.schema, yourPrompt.handler);
```

## Adding Resources

```ts
server.resource("example://data", "Example Resource", async () => ({
  contents: [{ uri: "example://data", text: "Resource content here" }]
}));
```

## HTTP Transport

This starter uses **stdio** (the standard for local MCP servers). If you need HTTP transport — for registries like [Smithery](https://smithery.ai)/[mcp.so](https://mcp.so) or remote deployments — use `StreamableHTTPServerTransport` with Express:

```ts
import express from 'express';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';

const app = express();
app.post('/mcp', async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  await server.connect(transport);
  await transport.handleRequest(req, res);
});
app.listen(3000);
```

See the [MCP SDK docs](https://github.com/modelcontextprotocol/typescript-sdk) for full details.

## Testing Locally

### MCP Inspector

```bash
npm run build
npx @modelcontextprotocol/inspector node dist/index.js
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "node",
      "args": ["/absolute/path/to/dist/index.js"]
    }
  }
}
```

### After Publishing to npm

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"]
    }
  }
}
```

## CI/CD

### CI (every push/PR)

1. Secret scanning (gitleaks)
2. Large file detection (>5 MB)
3. License compliance (blocks GPL/AGPL)
4. Security audit (`npm audit`)
5. Lint (ESLint + TypeScript)
6. Build (TypeScript compilation)
7. Test (Jest)

### CD (manual trigger)

1. CI gate (must pass)
2. Version guard (prevents duplicate releases)
3. npm publish with OIDC + provenance
4. GitHub Release

**Setup:** See [docs/NPM_PUBLISH_SETUP.md](docs/NPM_PUBLISH_SETUP.md)

## Project Structure

```
src/
├── index.ts              # Server entry — tool/prompt registration + transport
├── config.ts             # Environment variable config
├── helpers.ts            # ok() / err() response helpers
├── tools/
│   └── greet.ts          # Example tool with annotations (replace with your own)
└── prompts/
    └── hello.ts          # Example prompt (replace with your own)
tests/
├── greet.test.js         # Tool tests
├── helpers.test.js       # Helper tests
└── hello.test.js         # Prompt tests
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Run with tsx (no build needed) |
| `npm run build` | Compile TypeScript |
| `npm start` | Run compiled server |
| `npm test` | Build + run tests |
| `npm run lint` | ESLint |
| `npm run version:patch` | Bump patch version |

## License

MIT
