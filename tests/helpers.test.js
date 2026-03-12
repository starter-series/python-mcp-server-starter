import { describe, test, expect } from '@jest/globals';
import { ok, err } from '../dist/helpers.js';

describe('response helpers', () => {
  test('ok() wraps text in content array', () => {
    const result = ok('success');
    expect(result.content).toEqual([{ type: 'text', text: 'success' }]);
    expect(result).not.toHaveProperty('isError');
  });

  test('err() wraps text with isError flag', () => {
    const result = err('something failed');
    expect(result.content).toEqual([{ type: 'text', text: 'something failed' }]);
    expect(result.isError).toBe(true);
  });
});
