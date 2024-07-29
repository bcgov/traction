import { ExtendedV20CredExRecordByFormat, SchemaStorageRecord } from '@/types';
import {
  CredAttrSpec,
  CredDefStorageRecord,
  CredentialDefinition,
  TenantRecord,
  V20CredExRecord,
  V20CredExRecordDetail,
} from '@/types/acapyApi/acapyInterface';
import { Ref } from 'vue';
import { formatDateLong } from '.';

// Types of the records that go into table rows
export interface FormattedCredDef extends CredDefStorageRecord {
  created: string;
}
export interface FormattedSchema extends SchemaStorageRecord {
  created: string;
  credentialDefinitions: CredentialDefinition[];
}
export interface FormattedTenantRecord extends TenantRecord {
  created: string;
}
export interface FormattedHeldCredentialRecord extends V20CredExRecordDetail {
  credential_exchange_id?: string;
  connection?: string;
  created: string;
  credential_attributes: CredAttrSpec[];
  state: V20CredExRecord['state'];
}
export interface FormattedIssuedCredentialRecord extends V20CredExRecordDetail {
  connection?: string;
  connection_id?: string;
  created: string;
  cred_rev_id?: string;
  rev_reg_id?: string;
  state: V20CredExRecord['state'];
}

// Formatter functions to make rows for datatables from API/store lists
export const formatSchemaList = (
  schemaList: Ref<SchemaStorageRecord[]>
): FormattedSchema[] =>
  schemaList.value.map((schema: any) => ({
    schema: {
      name: schema.schema.name,
      version: schema.schema.version,
      attrNames: schema.schema.attrNames.sort(),
    },
    schema_id: schema.schema_id,
    created: formatDateLong(schema.created_at),
    created_at: schema.created_at,
    credentialDefinitions: schema.credentialDefinitions.sort(),
  }));

export const formatStoredCredDefs = (
  storedCredDefs: Ref<CredDefStorageRecord[]>
): FormattedCredDef[] =>
  storedCredDefs.value.map((credDef: any) => ({
    cred_def_id: credDef.cred_def_id,
    schema_id: credDef.schema_id,
    support_revocation: credDef.support_revocation,
    created_at: credDef.created_at,
    created: formatDateLong(credDef.created_at),
  }));

export const formatTenants = (
  tenants: Ref<TenantRecord[]>
): FormattedTenantRecord[] =>
  tenants.value.map((tenant: any) => ({
    deleted_at: formatDateLong(tenant.deleted_at),
    tenant_id: tenant.tenant_id,
    tenant_name: tenant.tenant_name,
    contact_email: tenant.contact_email,
    connect_to_endorser: tenant.connect_to_endorser,
    created_public_did: tenant.created_public_did,
    created: formatDateLong(tenant.created_at),
    created_at: tenant.created_at,
    enable_ledger_switch: tenant.enable_ledger_switch,
    state: tenant.state,
    curr_ledger_id: tenant.curr_ledger_id,
  }));

export const formatHeldCredentials = (
  credentials: Ref<V20CredExRecordDetail[]>,
  findConnectionName: (connectionId: string) => string | undefined
): FormattedHeldCredentialRecord[] =>
  credentials.value.map((ce) => ({
    credential_exchange_id: ce.cred_ex_record?.cred_ex_id,
    credential_attributes: getAttributes(ce),
    connection: findConnectionName(ce.cred_ex_record?.connection_id ?? ''),
    credential_definition_id: (
      ce.cred_ex_record?.by_format as ExtendedV20CredExRecordByFormat
    )?.cred_offer?.indy?.cred_def_id,
    state: ce.cred_ex_record?.state,
    updated: formatDateLong(ce.cred_ex_record?.updated_at ?? ''),
    updated_at: ce.cred_ex_record?.updated_at,
    created: formatDateLong(ce.cred_ex_record?.created_at ?? ''),
    created_at: ce.cred_ex_record?.created_at,
  }));

export const formatIssuedCredentials = (
  credentials: Ref<V20CredExRecordDetail[]>,
  findConnectionName: (connectionId: string) => string | undefined
): FormattedIssuedCredentialRecord[] =>
  credentials.value.map((ce) => ({
    state: ce.cred_ex_record?.state,
    cred_rev_id: ce.indy?.cred_rev_id,
    rev_reg_id: ce.indy?.rev_reg_id,
    connection_id: ce.cred_ex_record?.connection_id,
    connection: findConnectionName(ce.cred_ex_record?.connection_id ?? ''),
    credential_definition_id: (
      ce.cred_ex_record?.by_format as ExtendedV20CredExRecordByFormat
    )?.cred_offer?.indy?.cred_def_id,
    credential_exchange_id: ce.cred_ex_record?.cred_ex_id,
    created: formatDateLong(ce.cred_ex_record?.created_at),
    created_at: ce.cred_ex_record?.created_at,
  }));

// Helpers
const getAttributes = (data: V20CredExRecordDetail): CredAttrSpec[] => {
  return data.cred_ex_record?.cred_offer?.credential_preview?.attributes ?? [];
};
