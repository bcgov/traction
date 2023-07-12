import { vi } from 'vitest';

const store: { [key: string]: any } = {
  login: vi.fn().mockResolvedValue('success'),
};

export { store };
