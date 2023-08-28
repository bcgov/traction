const acceptInvite = {
  inviteUrl: {
    $invalid: false,
    required: {
      $message: 'Url is required',
    },
  },
  $invalid: false,
};

const acceptInviteSubmission = {
  invitationJson: {
    $invalid: false,
    required: {
      $message: 'Invalid JSON format',
    },
  },
  alias: {
    $invalid: false,
    required: {
      $message: 'Alias is required',
    },
  },
  $invalid: false,
};

const basicAlias = {
  alias: {
    value: 'test',
    $invalid: false,
    required: {
      $message: 'Alias is required',
    },
  },
  $invalid: false,
};

const createMessage = {
  msgContent: {
    $invalid: false,
    required: {
      $message: 'Message content is required',
    },
  },
  selectedConnection: {
    value: 'test',
    $invalid: false,
    required: {
      $message: 'Value is required',
    },
  },
  $invalid: false,
};

const didCreateRequest = {
  did: {
    $invalid: false,
    required: {
      $message: 'DID is required',
    },
  },
  alias: {
    $invalid: false,
    required: {
      $message: 'Alias is required',
    },
  },
  $invalid: false,
};

const login = {
  walletId: {
    $invalid: false,
    required: {
      $message: 'Wallet ID is required',
    },
  },
  walletSecret: {
    $invalid: false,
    required: {
      $message: 'Wallet Secret is required',
    },
  },
  tenantId: {
    $invalid: false,
    required: {
      $message: 'Tenant ID is required',
    },
  },
  apiKey: {
    $invalid: false,
    required: {
      $message: 'API Key is required',
    },
  },
  $invalid: false,
};

const innkeeperLogin = {
  adminName: {
    $invalid: false,
    required: {
      $message: 'Name is required',
    },
  },
  adminKey: {
    $invalid: false,
    required: {
      $message: 'Key is required',
    },
  },
  $invalid: false,
};

export {
  acceptInvite,
  acceptInviteSubmission,
  basicAlias,
  createMessage,
  didCreateRequest,
  innkeeperLogin,
  login,
};
