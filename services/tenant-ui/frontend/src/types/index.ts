// import { IndyCredInfo, V10CredentialExchange } from '@/types/acapyApi/acapyInterface';
// export interface CombinedCredentialAndExchange {
//   credential?: IndyCredInfo;
//   credentialExchange: V10CredentialExchange;
// }

import { Ref } from 'vue';
import {
  CredDefStorageRecord,
  SchemaStorageRecord as AcapySchemaStorageRecord,
  Schema,
  V20CredExRecordByFormat,
} from './acapyApi/acapyInterface';

export interface GetItem {
  item?: any;
  error?: Ref<String>;
  loading: boolean;
  fetchItem: (id?: string, params?: any) => Promise<void>;
}

export interface Attribute {
  name: string;
}

export interface AddSchemaFromLedgerRequest {
  schema_id: string;
}

// Extensions of things from the generated acapyInterface.ts types
// those come from an openAPI generator, and the ACA-Py API is not fully
// described in the openAPI spec for some things, so we extend some types
export interface StoredSchemaWithCredDefs extends SchemaStorageRecord {
  credentialDefinitions: CredDefStorageRecord[];
}
export interface SchemaStorageRecord extends AcapySchemaStorageRecord {
  schema: Schema;
}
// The Types in the cred exchange format are just "object"
export interface ExtendedV20CredExRecordByFormat
  extends V20CredExRecordByFormat {
  cred_offer?: {
    indy?: {
      cred_def_id?: string;
      schema_id?: string;
      key_correctness_proof?: any;
      nonce?: string;
    };
  };
}

export interface ServerConfig {
  config: {
    debug: {
      auto_respond_credential_request: boolean;
      auto_respond_presentation_proposal: boolean;
      auto_store_credential: boolean;
      auto_verify_presentation: boolean;
      auto_accept_invites: boolean;
      auto_accept_requests: boolean;
      auto_respond_messages: boolean;
      monitor_ping: boolean;
    };
    external_plugins: Array<string>;
    plugin_config: {
      multitenant_provider: {
        manager: {
          class_name: string;
          always_check_provided_wallet_key: boolean;
        };
        errors: {
          on_unneeded_wallet_key: boolean;
        };
        token_expiry: {
          units: string;
          amount: number;
        };
      };
      traction_innkeeper: {
        reservation: {
          auto_approve: boolean;
          expiry_minutes: number;
          auto_issuer: boolean;
        };
      };
      basicmessage_storage: {
        wallet_enabled: boolean;
      };
    };
    default_endpoint: string;
    additional_endpoints: Array<any>;
    tails_server_base_url: string;
    tails_server_upload_url: string;
    revocation: {
      notify: boolean;
      monitor_notification: boolean;
      anoncreds_legacy_support: string;
    };
    'ledger.ledger_config_list': Array<{
      id: string;
      is_production: boolean;
      is_write: boolean;
      genesis_transactions: string;
      keepalive: number;
      read_only: boolean;
      socks_proxy: any;
      pool_name: string;
      endorser_alias: string;
      endorser_did: string;
    }>;
    'ledger.keepalive': number;
    'ledger.read_only': boolean;
    'ledger.write_ledger': string;
    log: { level: string };
    auto_ping_connection: boolean;
    trace: {
      target: string;
      tag: string;
      label: string;
    };
    preserve_exchange_records: boolean;
    emit_new_didcomm_prefix: boolean;
    emit_new_didcomm_mime_type: boolean;
    auto_provision: boolean;
    transport: {
      inbound_configs: Array<Array<string>>;
      'transport.outbound_configs': ['http'];
      enable_undelivered_queue: boolean;
      max_message_size: number;
      max_outbound_retry: number;
      ws: { timeout_interval: number };
    };
    wallet: { type: string };
    multitenant: {
      enabled: boolean;
      admin_enabled: boolean;
      wallet_type: string;
      base_wallet_routes: Array<string>;
    };
    endorser: {
      author: boolean;
      endorser: boolean;
      auto_endorse: boolean;
      auto_write: boolean;
      auto_create_rev_reg: boolean;
      auto_promote_author_did: boolean;
      auto_request: boolean;
      endorser_alias: string;
      endorser_public_did: string;
    };
    version: string | undefined;
  };
}
