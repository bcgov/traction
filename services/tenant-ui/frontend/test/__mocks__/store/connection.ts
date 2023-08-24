import { vi } from 'vitest';

const connections = [
  {
    accept: 'auto',
    alias: 'test.alias',
    connection_id: 'bb6f8738-b3ee-46e4-b979-a84e6b269a0a',
    connection_protocol: 'connections/1.0',
    created_at: '2023-06-26T22:28:19.163437Z',
    invitation_key: 'B6nQE8AjZHoYC3VgDapLGbD8iZJ6cHAepMq3evLaq6hg',
    invitation_mode: 'once',
    my_did: 'BEQWiPfQXj9q9DYePziaJ2',
    rfc23_state: 'completed',
    routing_state: 'none',
    state: 'active',
    their_did: 'Tr23L12egq68Ei3Q8uYAeg',
    their_label: 'BC Wallet',
    their_role: 'invitee',
    updated_at: '2023-06-26T22:28:49.084854Z',
  },
];

const store: { [key: string]: any } = {
  connections: {
    value: connections,
  },
  connectionsDropdown: [
    {
      label: 'endorser',
      value: '7dcfd983-71f9-4a05-a13b-a2026ed85bb9',
      status: 'active',
    },
  ],
  createInvitation: vi.fn().mockResolvedValue({
    invitation_url: 'test_invitation_url',
  }),
  didCreateRequest: vi.fn().mockResolvedValue({}),
  filteredConnections: {
    value: connections,
  },
  filteredInvitations: {
    value: connections,
  },
  getInvitation: vi.fn().mockResolvedValue({
    invitation_url: 'test_invitation_url',
  }),
  listConnections: vi
    .fn()
    .mockResolvedValue([
      {
        connection_id: 'bb6f8738-b3ee-46e4-b979-a84e6b269a0a',
      },
    ])
    .mockRejectedValue([]),
  updateConnection: vi.fn().mockResolvedValue({}),
  receiveInvitation: vi.fn().mockResolvedValue({
    invitation_url: 'test_invitation_url',
  }),
  findConnectionName: vi.fn().mockReturnValue('test-name'),
};

export { store };
