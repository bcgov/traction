import { vi } from 'vitest';

const store: { [key: string]: any } = {
  clearToken: vi.fn(),
  innkeeperReady: vi.fn().mockResolvedValue(false),
  login: vi.fn().mockResolvedValue('success'),
};

export { store };
