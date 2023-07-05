import { vi } from 'vitest';

const store: { [key: string]: any } = {
  messages: {
    value: [
      {
        connection_id: '123',
        content: 'test',
        created_at: '"2023-06-26T22:34:14.058181Z"',
        message_id: '123',
        sent_time: '"2023-06-26T22:34:14.058181Z"',
        state: 'received',
        updated_at: '"2023-06-26T22:34:14.058181Z"',
      },
    ],
  },
  selectedMessage: null,
  loading: false,
  error: null,
  newMessage: '',
};

store.listMessages = vi.fn().mockResolvedValue([
  {
    connection_id: 'test-connection-id',
    content: 'test-content',
    created_at: '2023-07-04T17:16:13.771616Z',
    displayTime: true,
    message_id: '7f0ba8a4-c798-402d-895a-d68c777ea294',
    sent_time: '2023-07-04T17:16:13.769151Z',
    state: 'sent',
    updated_at: '2023-07-04T17:16:13.771616Z',
  },
]);

store.sendMessage = vi.fn().mockResolvedValue(true);

export { store };
