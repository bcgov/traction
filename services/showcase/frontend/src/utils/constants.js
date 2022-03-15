//
// Constants
//

/** API Route paths */
export const ApiRoutes = Object.freeze({
  BASEPATH: '/api/v1',
  SANDBOXES: '/sandboxes',
  WEBHOOK: '/webhook'
});

/** Corresponds to vuetify alert classes for notification types */
export const NotificationTypes = Object.freeze({
  ERROR: 'error',
  SUCCESS: 'success',
  INFO: 'info',
  WARNING: 'warning',
});

export const Regex = Object.freeze({
  // From ajv-format
  EMAIL: '^[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\\.[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$'
});

/** Our showcase tenants */
export const Tenants = Object.freeze({
  ALICE: 'Alice',
  ACME: 'Acme',
  FABER: 'Faber'
});
