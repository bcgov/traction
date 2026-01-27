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
import { formatDateLong, truncateId } from '.';

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
): FormattedSchema[] => {
  // Safety check - ensure schemaList.value exists and is an array
  if (!schemaList.value || !Array.isArray(schemaList.value)) {
    return [];
  }

  return schemaList.value
    .filter((schema: any) => {
      // Filter out null, undefined, or invalid schemas
      if (!schema || typeof schema !== 'object') {
        return false;
      }
      // Must have schema_id
      if (!schema.schema_id) {
        return false;
      }
      // Must have schema object with at least name property
      if (!schema.schema || typeof schema.schema !== 'object') {
        return false;
      }
      // Only show active schemas (or schemas without state set)
      // state can be 'active' or 'deleted' from the API
      if (schema.state === 'deleted') {
        return false;
      }
      return true;
    })
    .map((schema: any) => {
      // Defensive checks - ensure schema.schema exists (already filtered, but double-check)
      const schemaObj = schema.schema;
      if (!schemaObj || typeof schemaObj !== 'object') {
        // Return a safe default
        return {
          schema: {
            name: 'Invalid',
            version: 'Unknown',
            attrNames: [],
          },
          schema_id: schema.schema_id || 'Unknown',
          created: formatDateLong(schema.created_at),
          created_at: schema.created_at,
          credentialDefinitions: [],
        };
      }

      return {
        schema: {
          name: schemaObj.name || 'Unknown',
          version: schemaObj.version || 'Unknown',
          attrNames: Array.isArray(schemaObj.attrNames)
            ? [...schemaObj.attrNames].sort()
            : [],
          // Preserve issuerId if present (for AnonCreds schemas)
          ...(schemaObj.issuerId && { issuerId: schemaObj.issuerId }),
        },
        schema_id: schema.schema_id || 'Unknown',
        created: formatDateLong(schema.created_at),
        created_at: schema.created_at,
        credentialDefinitions: Array.isArray(schema.credentialDefinitions)
          ? [...schema.credentialDefinitions].sort()
          : [],
        // Preserve schema_dict if present (contains full schema data)
        ...(schema.schema_dict && { schema_dict: schema.schema_dict }),
      };
    });
};

export const formatStoredCredDefs = (
  storedCredDefs: Ref<CredDefStorageRecord[]>
): FormattedCredDef[] =>
  storedCredDefs.value.map((credDef: any) => ({
    cred_def_id: credDef.cred_def_id,
    schema_id: credDef.schema_id,
    tag: credDef.tag || '',
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
  findConnectionName: (connectionId: string) => string | undefined,
  storedCredDefs?: Ref<CredDefStorageRecord[]>
): FormattedIssuedCredentialRecord[] =>
  credentials.value.map((ce) => {
    const byFormat = ce.cred_ex_record
      ?.by_format as ExtendedV20CredExRecordByFormat;
    // Check both indy and anoncreds formats for credential definition ID
    const credDefId =
      byFormat?.cred_offer?.indy?.cred_def_id ||
      byFormat?.cred_offer?.anoncreds?.cred_def_id;

    // Check both indy and anoncreds for revocation info
    const credRevId = ce.indy?.cred_rev_id || ce.anoncreds?.cred_rev_id;
    const revRegId = ce.indy?.rev_reg_id || ce.anoncreds?.rev_reg_id;

    // Look up the credential definition to get the tag
    let credentialDefinitionDisplay = credDefId
      ? truncateId(credDefId)
      : credDefId;
    if (credDefId && storedCredDefs?.value) {
      const credDef = storedCredDefs.value.find(
        (cd) => cd.cred_def_id === credDefId
      );
      if (credDef?.tag) {
        // Format as "tag (truncated_id)"
        credentialDefinitionDisplay = `${credDef.tag} (${truncateId(credDefId)})`;
      }
    }

    const connectionId = ce.cred_ex_record?.connection_id ?? '';
    // findConnectionName is a function that takes connectionId and returns the connection name
    // It should use alias first, then their_label as fallback
    const connectionName = connectionId && findConnectionName 
      ? (findConnectionName(connectionId) || '')
      : '';
    
    return {
      // Preserve the full V20CredExRecordDetail structure for format detection
      ...ce,
      // Explicitly set all formatted values to ensure they override any spread properties
      state: ce.cred_ex_record?.state,
      cred_rev_id: credRevId,
      rev_reg_id: revRegId,
      connection_id: connectionId,
      connection: connectionName,
      credential_definition_id: credentialDefinitionDisplay,
      credential_exchange_id: ce.cred_ex_record?.cred_ex_id,
      created: formatDateLong(ce.cred_ex_record?.created_at),
      created_at: ce.cred_ex_record?.created_at,
    };
  });

// Helpers
const getAttributes = (data: V20CredExRecordDetail): CredAttrSpec[] => {
  return data.cred_ex_record?.cred_offer?.credential_preview?.attributes ?? [];
};
