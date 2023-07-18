import { vi } from 'vitest';

const store: { [key: string]: any } = {
  messages: {
    value: [
      {
        connection_id: 'test-connection-id',
        content: 'test-content',
        created_at: '2023-07-04T17:16:13.771616Z',
        displayTime: true,
        message_id: '7f0ba8a4-c798-402d-895a-d68c777ea294',
        sent_time: '2023-07-04T17:16:13.769151Z',
        state: 'sent',
        updated_at: '2023-07-04T17:16:13.771616Z',
        test: 'test',
      },
    ],
  },
  listMessages: vi.fn().mockResolvedValue([
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
  ]),
  newMessage: '',
  selectedMessage: null,
  sendMessage: vi.fn().mockResolvedValue(true),
};

export { store };
