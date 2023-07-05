import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll } from 'vitest';

// Import Handlers
import {
  acapyAuthErrorHandlers,
  acapySuccessHandlers,
  acapyUnknownErrorHandlers,
  contactsSuccessHandlers,
  contactsUnknownErrorHandlers,
  configSuccessHandlers,
  configUnknownErrorHandlers,
  governanceSuccessHandlers,
  governanceUnknownErrorHandlers,
  issuerSuccessHandlers,
  issuerUnknownErrorHandlers,
  messageSuccessHandlers,
  messageUnknownErrorHandlers,
  reservationSuccessHandlers,
  reservationUnknownErrorHandlers,
  tenantSuccessHandlers,
  tokenSuccessHandlers,
  tokenUnknownErrorHandlers,
  verifierSuccessHandlers,
} from './__mocks__/api/routes';

// Setup Server
export const restHandlers = [
  ...acapySuccessHandlers,
  ...contactsSuccessHandlers,
  ...configSuccessHandlers,
  ...governanceSuccessHandlers,
  ...issuerSuccessHandlers,
  ...messageSuccessHandlers,
  ...reservationSuccessHandlers,
  ...tenantSuccessHandlers,
  ...tokenSuccessHandlers,
  ...verifierSuccessHandlers,
];

export const restHandlersAuthorizationError = [...acapyAuthErrorHandlers];

export const restHandlersUnknownError = [
  ...acapyUnknownErrorHandlers,
  ...contactsUnknownErrorHandlers,
  ...configUnknownErrorHandlers,
  ...governanceUnknownErrorHandlers,
  ...issuerUnknownErrorHandlers,
  ...messageUnknownErrorHandlers,
  ...reservationUnknownErrorHandlers,
  ...tokenUnknownErrorHandlers,
];

export const server = setupServer(...restHandlers);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

afterAll(() => server.close());

afterEach(() => server.resetHandlers());
