import { vi } from 'vitest';

const store: { [key: string]: any } = {
  resetState: vi.fn(),
  status: {
    value: '',
  },
};

export { store };
