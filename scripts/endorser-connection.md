To use the endorser agent in this project the following steps need to happen. Through swagger pages. 

1. Generate invitation from endorser (POST `/connections/create_invitation`, receive invitation from tenant `/connections/recieve-invitation`

1. Set author/tenant's connection to endorser with the following. POST to `/connections/{conn_id}/metadata`
```
{
  "metadata": {
   "endorser_info":{
	   "endorser_did":"SVfHGCEEvEFmpBPcxgNqRR",
	   "endorser_name":"endorser"	
		},
   "transaction_jobs": {
      "transaction_their_job": "TRANSACTION_ENDORSER",
      "transaction_my_job": "TRANSACTION_AUTHOR"
    }
	}
}

```

3. Set endorsers connection to author/tenant with the following. POST to `/connections/{conn_id}/metadata`
```
{
  "metadata":{
    "transaction_jobs": {
      "transaction_my_job": "TRANSACTION_ENDORSER",
      "transaction_their_job": "TRANSACTION_AUTHOR"
    }
  }
}
```

4. Out Of Band: in Endorser POST the tenant did/verkey to `/ledger/register-nym`.
1. In Author/Tenant POST to `wallet/did/public` to set that did as public

Now when the tenant executes and action that requires a ledger write (e.g. schema/cred def creation), it will automatically send it to the endorser, and the endorser will automatically sign it and send it back!!
