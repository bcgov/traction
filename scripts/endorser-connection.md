To use the endorser agent in this project the following steps need to happen. Through swagger pages. 

1. Generate invitation from endorser (POST `/connections/create_invitation`, receive invitation from tenant `/connections/recieve-invitation`

1. Set author/tenant's connection to endorser with the following. 
    - POST to `/transactions/{conn_id}/set-endorser-info`  with endorsers did and name
    - POST to `/transactions/{conn_id}/set-endorser-role`  as `TRANSACTION_AUTHOR`.


1. Set endorsers connection to author/tenant with the following. POST to `/transactions/{conn_id}/set-endorser-role` as `TRANSACTION_ENDORSER`

1. Out Of Band: Get tenant did/verkey from (with bearer token) GET `wallet/did` and POST that did/verkey to Endorser swagger at `/ledger/register-nym`. 
1. In Author/Tenant POST to `wallet/did/public` to set that did as public

Now when the tenant executes and action that requires a ledger write (e.g. schema/cred def creation), it will automatically send it to the endorser, and the endorser will automatically sign it and send it back!!
