import { describe, test, expect } from '@jest/globals';
import { handler } from '../dist/prompts/hello.js';

describe('hello prompt', () => {
  test('returns English greeting by default', () => {
    const result = handler({});
    expect(result.messages[0].role).toBe('user');
    expect(result.messages[0].content.text).toBe('Write a friendly greeting.');
  });

  test('returns Korean greeting', () => {
    const result = handler({ language: 'ko' });
    expect(result.messages[0].content.text).toContain('인사말');
  });

  test('includes description', () => {
    const result = handler({});
    expect(result.description).toBeDefined();
  });
});
