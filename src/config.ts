/**
 * Environment variable configuration.
 * Add your server's config options here.
 */

export interface ServerConfig {
  /** Enable debug logging to stderr. Default: false */
  debug: boolean;
}

export function parseConfig(): ServerConfig {
  return {
    debug: process.env.MCP_DEBUG === 'true',
  };
}
