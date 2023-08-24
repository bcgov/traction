import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll } from 'vitest';

// Import Handlers
import {
  acapyAuthErrorHandlers,
  acapySuccessHandlers,
  acapyUnknownErrorHandlers,
  connectionSuccessHandlers,
  connectionUnknownErrorHandlers,
  configSuccessHandlers,
  configUnknownErrorHandlers,
  holderSuccessHandlers,
  holderUnknownErrorHandlers,
  governanceSuccessHandlers,
  governanceUnknownErrorHandlers,
  issuerSuccessHandlers,
  issuerUnknownErrorHandlers,
  messageSuccessHandlers,
  messageUnknownErrorHandlers,
  reservationSuccessHandlers,
  reservationUnknownErrorHandlers,
  tenantSuccessHandlers,
  tenantUnknownErrorHandlers,
  tokenSuccessHandlers,
  tokenUnknownErrorHandlers,
  verifierSuccessHandlers,
  verifierUnknownErrorHandlers,
  // Innkeeper
  innkeeperTokenSuccessHandlers,
  innkeeperTokenUnknownErrorHandlers,
  innkeeperTenantSuccessHandlers,
  innkeeperTenantUnknownErrorHandlers,
} from './__mocks__/api/routes';

// Setup Server
export const restHandlers = [
  ...acapySuccessHandlers,
  ...connectionSuccessHandlers,
  ...configSuccessHandlers,
  ...holderSuccessHandlers,
  ...governanceSuccessHandlers,
  ...issuerSuccessHandlers,
  ...messageSuccessHandlers,
  ...reservationSuccessHandlers,
  ...tenantSuccessHandlers,
  ...tokenSuccessHandlers,
  ...verifierSuccessHandlers,
  // Innkeeper
  ...innkeeperTokenSuccessHandlers,
  ...innkeeperTenantSuccessHandlers,
];

export const restHandlersAuthorizationError = [...acapyAuthErrorHandlers];

export const restHandlersUnknownError = [
  ...acapyUnknownErrorHandlers,
  ...connectionUnknownErrorHandlers,
  ...configUnknownErrorHandlers,
  ...holderUnknownErrorHandlers,
  ...governanceUnknownErrorHandlers,
  ...issuerUnknownErrorHandlers,
  ...messageUnknownErrorHandlers,
  ...reservationUnknownErrorHandlers,
  ...tenantUnknownErrorHandlers,
  ...tokenUnknownErrorHandlers,
  ...verifierUnknownErrorHandlers,
  // Innkeeper
  ...innkeeperTokenUnknownErrorHandlers,
  ...innkeeperTenantUnknownErrorHandlers,
];

export const server = setupServer(...restHandlers);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

afterAll(() => server.close());

afterEach(() => server.resetHandlers());
