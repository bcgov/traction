import { vi } from 'vitest';

const store: { [key: string]: any } = {
  innkeeperReady: vi.fn().mockResolvedValue(false),
  login: vi.fn().mockResolvedValue('success'),
};

export { store };
