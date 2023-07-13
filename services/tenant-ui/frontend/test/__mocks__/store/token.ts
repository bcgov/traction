import { vi } from 'vitest';

const store: { [key: string]: any } = {
  login: vi.fn().mockResolvedValue({}),
  token: {
    value: 'token',
  },
};

export { store };
