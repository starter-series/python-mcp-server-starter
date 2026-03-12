> **[Starter Series](https://github.com/heznpc/starter-series)** — 매번 AI한테 CI/CD 설명하지 마세요. Clone하고 바로 시작하세요.
>
> [Docker 배포](https://github.com/heznpc/docker-deploy-starter) · [Discord 봇](https://github.com/heznpc/discord-bot-starter) · [Telegram 봇](https://github.com/heznpc/telegram-bot-starter) · [브라우저 확장](https://github.com/heznpc/browser-extension-starter) · [Electron 앱](https://github.com/heznpc/electron-app-starter) · [npm 패키지](https://github.com/heznpc/npm-package-starter) · [React Native](https://github.com/heznpc/react-native-starter) · [VS Code 확장](https://github.com/heznpc/vscode-extension-starter) · **MCP 서버**

**English** → [README.md](README.md)

# MCP Server Starter

프로덕션 레디 [Model Context Protocol](https://modelcontextprotocol.io) 서버 템플릿. CI/CD, 보안 검사, npm 배포가 내장되어 있습니다.

## 포함 사항

- **MCP SDK** — `@modelcontextprotocol/sdk` + stdio 트랜스포트
- **TypeScript** — Strict 모드, ES2022, Zod 스키마 검증
- **Safety Annotations** — 모든 도구에 readOnly/destructive/idempotent 힌트
- **Prompts** — 가이드 워크플로우 템플릿
- **응답 헬퍼** — `ok()`과 `err()`로 일관된 도구 응답
- **Config** — 환경변수 파싱 패턴
- **CI** — gitleaks, npm audit, 라이선스 검사, ESLint, 빌드, 테스트
- **CD** — OIDC trusted publishing으로 npm 배포 (시크릿 0개)
- **Dependabot** — 의존성 + GitHub Actions 자동 업데이트

## 빠른 시작

```bash
git clone https://github.com/heznpc/mcp-server-starter.git my-mcp-server
cd my-mcp-server
rm -rf .git && git init

npm install
npm run dev
```

## Tool 추가

`src/tools/your-tool.ts` 생성:

```ts
import { z } from 'zod';
import { ok, err } from '../helpers.js';

export const name = 'your_tool';

export const config = {
  title: 'Your Tool',
  description: 'Tool 설명',
  inputSchema: {
    input: z.string().describe('입력 파라미터'),
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
    return ok(`결과: ${input}`);
  } catch (e) {
    return err(`실패: ${e instanceof Error ? e.message : String(e)}`);
  }
}
```

`src/index.ts`에 등록:

```ts
import * as yourTool from './tools/your-tool.js';
server.registerTool(yourTool.name, yourTool.config, yourTool.handler);
```

## Prompt 추가

`src/prompts/your-prompt.ts` 생성:

```ts
import { z } from 'zod';

export const name = 'your-prompt';
export const description = '가이드 워크플로우 설명';

export const schema = {
  param: z.string().optional().describe('선택 파라미터'),
};

export function handler({ param }: { param?: string }) {
  return {
    description,
    messages: [{
      role: 'user' as const,
      content: { type: 'text' as const, text: `프롬프트 텍스트 ${param ?? '기본값'}` },
    }],
  };
}
```

`src/index.ts`에 등록:

```ts
import * as yourPrompt from './prompts/your-prompt.js';
server.prompt(yourPrompt.name, yourPrompt.description, yourPrompt.schema, yourPrompt.handler);
```

## 로컬 테스트

### MCP Inspector

```bash
npm run build
npx @modelcontextprotocol/inspector node dist/index.js
```

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "node",
      "args": ["/절대/경로/dist/index.js"]
    }
  }
}
```

### npm 배포 후

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

### CI (매 push/PR)

1. 시크릿 스캔 (gitleaks)
2. 대용량 파일 감지 (>5 MB)
3. 라이선스 검사 (GPL/AGPL 차단)
4. 보안 감사 (`npm audit`)
5. 린트 (ESLint + TypeScript)
6. 빌드 (TypeScript 컴파일)
7. 테스트 (Jest)

### CD (수동 트리거)

1. CI 통과 필수
2. 버전 중복 방지 (version guard)
3. OIDC + provenance로 npm 배포
4. GitHub Release 생성

**설정:** [docs/NPM_PUBLISH_SETUP.md](docs/NPM_PUBLISH_SETUP.md) 참고

## 프로젝트 구조

```
src/
├── index.ts              # 서버 진입점 — Tool/Prompt 등록 + 트랜스포트
├── config.ts             # 환경변수 설정
├── helpers.ts            # ok() / err() 응답 헬퍼
├── tools/
│   └── greet.ts          # 예시 Tool + annotations (교체해서 사용)
└── prompts/
    └── hello.ts          # 예시 Prompt (교체해서 사용)
tests/
├── greet.test.js         # Tool 테스트
├── helpers.test.js       # 헬퍼 테스트
└── hello.test.js         # Prompt 테스트
```

## 스크립트

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | tsx로 실행 (빌드 불필요) |
| `npm run build` | TypeScript 컴파일 |
| `npm start` | 컴파일된 서버 실행 |
| `npm test` | 빌드 + 테스트 |
| `npm run lint` | ESLint |
| `npm run version:patch` | 패치 버전 올리기 |

## 라이선스

MIT
