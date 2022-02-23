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
  ERROR: {
    type: 'error',
    class: 'alert-error',
    icon: 'error',
  },
  SUCCESS: {
    type: 'success',
    class: 'alert-success',
    icon: 'check_circle',
  },
  INFO: {
    type: 'info',
    class: 'alert-info',
    icon: 'info',
  },
  WARNING: {
    type: 'warning',
    class: 'alert-warning',
    icon: 'warning',
  },
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
