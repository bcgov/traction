import { vi } from 'vitest';

const store: { [key: string]: any } = {
  clearToken: vi.fn(),
  login: vi.fn().mockResolvedValue({}),
  token: {
    value: 'token',
  },
};

export { store };
