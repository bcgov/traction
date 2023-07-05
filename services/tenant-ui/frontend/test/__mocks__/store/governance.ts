const store: { [key: string]: any } = {
  contacts: [
    {
      accept: 'auto',
      state: 'active',
      my_did: 'BEQWiPfQXj9q9DYePziaJ2',
      connection_id: 'bb6f8738-b3ee-46e4-b979-a84e6b269a0a',
      invitation_key: 'B6nQE8AjZHoYC3VgDapLGbD8iZJ6cHAepMq3evLaq6hg',
      invitation_mode: 'once',
      routing_state: 'none',
      alias: 'test',
      their_did: 'Tr23L12egq68Ei3Q8uYAeg',
      updated_at: '2023-06-26T22:28:49.084854Z',
      their_label: 'BC Wallet',
      rfc23_state: 'completed',
      created_at: '2023-06-26T22:28:19.163437Z',
      connection_protocol: 'connections/1.0',
      their_role: 'invitee',
    },
  ],
  contactsDropdown: [
    {
      label: 'endorser',
      value: '7dcfd983-71f9-4a05-a13b-a2026ed85bb9',
      status: 'active',
    },
  ],
  selectedContact: null,
  loading: false,
  loadingItem: false,
  error: null,
  filteredConnections: {
    value: [],
  },
  filteredInvitations: {
    value: [],
  },
};

export { store };
