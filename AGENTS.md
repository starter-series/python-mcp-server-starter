# AGENTS.md

> This file provides context for AI coding assistants (Claude Code, Cursor, Copilot, Cline, etc.)

## Project Structure

```
src/
├── index.ts              # Server entry point — registers tools/prompts and starts transport
├── config.ts             # Environment variable parsing
├── helpers.ts            # Response helpers: ok() and err()
├── tools/
│   └── greet.ts          # Example tool with safety annotations — copy this pattern
└── prompts/
    └── hello.ts          # Example prompt — copy this pattern
tests/
├── greet.test.js         # Tool tests (run against built output in dist/)
├── helpers.test.js       # Helper tests
└── hello.test.js         # Prompt tests
```

## Adding a New Tool

1. Create `src/tools/your-tool.ts`:
   ```ts
   import { z } from 'zod';
   import { ok, err } from '../helpers.js';

   export const name = 'your_tool';

   export const config = {
     title: 'Your Tool',
     description: 'What your tool does',
     inputSchema: {
       param: z.string().describe('Parameter description'),
     },
     annotations: {
       readOnlyHint: true,       // Does not modify anything
       destructiveHint: false,    // Not destructive
       idempotentHint: true,      // Same input = same result
       openWorldHint: false,      // No external system interaction
     },
   };

   export async function handler({ param }: { param: string }) {
     try {
       return ok(`Result: ${param}`);
     } catch (e) {
       return err(`Failed: ${e instanceof Error ? e.message : String(e)}`);
     }
   }
   ```
2. Register it in `src/index.ts`:
   ```ts
   import * as yourTool from './tools/your-tool.js';
   server.registerTool(yourTool.name, yourTool.config, yourTool.handler);
   ```
3. Add tests in `tests/your-tool.test.js`

## Adding a New Prompt

1. Create `src/prompts/your-prompt.ts`:
   ```ts
   import { z } from 'zod';

   export const name = 'your-prompt';
   export const description = 'What the prompt does';

   export const schema = {
     param: z.string().optional().describe('Optional parameter'),
   };

   export function handler({ param }: { param?: string }) {
     return {
       description,
       messages: [
         {
           role: 'user' as const,
           content: { type: 'text' as const, text: `Your prompt text with ${param ?? 'default'}` },
         },
       ],
     };
   }
   ```
2. Register it in `src/index.ts`:
   ```ts
   import * as yourPrompt from './prompts/your-prompt.js';
   server.prompt(yourPrompt.name, yourPrompt.description, yourPrompt.schema, yourPrompt.handler);
   ```

## Safety Annotations

Every tool should declare annotations to help AI clients handle them safely:

| Annotation | Meaning | Example |
|------------|---------|---------|
| `readOnlyHint: true` | Does not modify anything | search, list, read |
| `destructiveHint: true` | May cause irreversible changes | delete, overwrite |
| `idempotentHint: true` | Repeated calls have same effect | update, create-if-not-exists |
| `openWorldHint: true` | Interacts with external systems | API calls, network requests |

## Scaling to Multi-Module

For larger servers with multiple service domains:

```
src/
├── index.ts
├── config.ts
├── helpers.ts
├── notes/              # Module A
│   ├── tools.ts
│   ├── scripts.ts
│   └── prompts.ts
├── calendar/           # Module B
│   ├── tools.ts
│   └── prompts.ts
└── shared/             # Cross-module utilities
    └── jxa.ts
```

Each module exports a `registerXxxTools(server, config)` function called from `index.ts`.

## CI/CD Pipeline

- **CI** (`ci.yml`): gitleaks → large file check → npm ci → license check → audit → lint → build → test
- **CD** (`cd.yml`): CI gate → version guard → npm publish (OIDC) → GitHub Release

## Key Patterns

- Tools use `registerTool(name, config, handler)` with annotations
- Prompts use `server.prompt(name, description, schema, handler)`
- Response helpers: `ok(text)` for success, `err(message)` for errors — tools should never throw
- Config parsed from environment variables in `config.ts`
- Zod schemas validate tool/prompt inputs at runtime
- `StdioServerTransport` for CLI/desktop usage (npx)
- Tests import from `dist/` (built output) — run `npm run build` before testing
- Use `.js` extensions in TypeScript imports (required for Node16 module resolution)

## Do NOT Modify

- `.github/workflows/` CI/CD pipeline structure
  - **Why**: Version guard, OIDC publishing, and CI gate protect against duplicate releases and untested deploys
- `tsconfig.json` module settings (`Node16`)
  - **Why**: Required for ESM + Node.js interop. Changing breaks `.js` extension imports
