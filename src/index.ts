import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { parseConfig } from './config.js';
import * as greet from './tools/greet.js';
import * as hello from './prompts/hello.js';

const config = parseConfig();

const server = new McpServer({
  name: 'my-mcp-server',
  version: '1.0.0',
});

// Tools — use registerTool for full control (annotations, title)
server.registerTool(greet.name, greet.config, greet.handler);

// Prompts — guided workflows for common tasks
server.prompt(hello.name, hello.description, hello.schema, hello.handler);

const transport = new StdioServerTransport();
await server.connect(transport);

if (config.debug) {
  console.error('MCP server running on stdio');
}
