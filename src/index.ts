#!/usr/bin/env node
import { createRequire } from 'node:module';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { parseConfig } from './config.js';
import * as greet from './tools/greet.js';
import * as hello from './prompts/hello.js';

const require = createRequire(import.meta.url);
const { name, version } = require('../package.json') as { name: string; version: string };

const config = parseConfig();

const server = new McpServer({
  name,
  version,
});

// Tools — use registerTool for full control (annotations, title)
server.registerTool(greet.name, greet.config, greet.handler);
// To pass config to tool handlers in multi-module setups:
// import { registerNoteTools } from './notes/tools.js';
// registerNoteTools(server, config);

// Resources — expose data to the client (replace with your own)
server.resource("example://data", "Example Resource", async () => ({
  contents: [{ uri: "example://data", text: "Replace with your resource data" }],
}));

// Prompts — guided workflows for common tasks
server.prompt(hello.name, hello.description, hello.schema, hello.handler);

const transport = new StdioServerTransport();

try {
  await server.connect(transport);
} catch (error) {
  console.error('Failed to connect MCP server:', error);
  process.exit(1);
}

if (config.debug) {
  console.error('MCP server running on stdio');
}

const shutdown = async () => {
  await transport.close();
  process.exit(0);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
