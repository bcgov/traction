import { vi } from 'vitest';

const store: { [key: string]: any } = {
  contacts: {
    value: [
      {
        accept: 'auto',
        alias: 'test',
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
    ],
  },
};

store.listContacts = vi
  .fn()
  .mockResolvedValue([
    {
      connection_id: 'bb6f8738-b3ee-46e4-b979-a84e6b269a0a',
    },
  ])
  .mockRejectedValue([]);

store.createInvitation = vi.fn().mockResolvedValue({
  invitation_url: 'test_invitation_url',
});

store.listContacts = vi.fn().mockResolvedValue([
  {
    connection_id: 'bb6f8738-b3ee-46e4-b979-a84e6b269a0a',
  },
]);

store.didCreateRequest = vi.fn().mockResolvedValue({});

export { store };
