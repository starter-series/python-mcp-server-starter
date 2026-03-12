import { z } from 'zod';
import { ok } from '../helpers.js';

export const name = 'greet';

export const config = {
  title: 'Greet',
  description: 'Greet someone by name',
  inputSchema: {
    name: z.string().describe('Name to greet'),
  },
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: false,
  },
};

export async function handler({ name }: { name: string }) {
  return ok(`Hello, ${name}!`);
}
