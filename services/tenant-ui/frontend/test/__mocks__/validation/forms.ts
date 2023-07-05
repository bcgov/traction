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
  selectedContact: {
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
    $model: 'test',
    $invalid: false,
    required: {
      $message: 'Wallet ID is required',
    },
  },
  walletSecret: {
    $model: 'test',
    $invalid: false,
    required: {
      $message: 'Wallet Secret is required',
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
  login,
};
