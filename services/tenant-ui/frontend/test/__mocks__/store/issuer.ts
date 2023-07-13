import { vi } from 'vitest';

const store: { [key: string]: any } = {
  credentials: {
    value: [],
  },
  listCredentials: vi.fn().mockResolvedValue([]),
  selectedCredential: null,
};

export { store };
