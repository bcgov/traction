import { SchemaStorageRecord } from '@/types';
import {
  CredDefStorageRecord,
  CredentialDefinition,
  TenantRecord,
} from '@/types/acapyApi/acapyInterface';
import { Ref } from 'vue';
import { formatDateLong } from '.';

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
