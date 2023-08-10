import { createPinia, setActivePinia } from 'pinia';
import { beforeAll, beforeEach, describe, expect, test } from 'vitest';

import { useMessageStore } from '@/store/messageStore';
import { restHandlersUnknownError, server } from '../setupApi';
import { testErrorResponse, testSuccessResponse } from '../../test/commonTests';

let store: any;

describe('messageStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useMessageStore();
  });

  test("initial values haven't changed from expected", () => {
    expect(store.messages).toEqual([]);
    expect(store.selectedMessage).toEqual(null);
    expect(store.loading).toEqual(false);
    expect(store.error).toEqual(null);
    expect(store.newMessage).toEqual('');
  });

  describe('Successful API calls', () => {
    test('post sendMessage does not throw exception and sets loading correctly', async () => {
      await testSuccessResponse(
        store,
        store.sendMessage('connId', { content: 'test' }),
        'loading'
      );
    });

    test('get listMessages returns the expected values and sets loading correctly', async () => {
      let response = store.listMessages();
      await testSuccessResponse(store, response, 'loading');
      response = await response;
      expect(response).toHaveLength(2);
    });
  });

  describe('Unsuccessful API calls', () => {
    beforeAll(() => {
      server.use(...restHandlersUnknownError);
    });

    test('error responses are handled correctly', async () => {
      await testErrorResponse(
        store,
        store.sendMessage('connId', { content: 'test' }),
        'loading'
      );
    });
  });
});
