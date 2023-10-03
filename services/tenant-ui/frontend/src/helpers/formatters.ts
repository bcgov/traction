import {
  CredDefStorageRecord,
  CredentialDefinition,
  SchemaStorageRecord,
} from '@/types/acapyApi/acapyInterface';
import { formatDateLong } from '.';
import { Ref } from 'vue';

export interface FormattedSchema extends SchemaStorageRecord {
  created: string;
  credentialDefinitions: CredentialDefinition[];
}

export interface FormattedCredDef extends CredDefStorageRecord {
  created: string;
}

export const formattSchemaList = (
  schemaList: Ref<SchemaStorageRecord[]>
): FormattedSchema[] =>
  schemaList.value.map((schema: any) => ({
    schema: {
      name: schema.schema.name,
      version: schema.schema.version,
      attrNames: schema.schema.attrNames,
    },
    schema_id: schema.schema_id,
    created: formatDateLong(schema.created_at),
    created_at: schema.created_at,
    credentialDefinitions: schema.credentialDefinitions,
  }));

export const formattStoredCredDefs = (
  storedCredDefs: Ref<CredDefStorageRecord[]>
): FormattedCredDef[] =>
  storedCredDefs.value.map((credDef: any) => ({
    cred_def_id: credDef.cred_def_id,
    schema_id: credDef.schema_id,
    support_revocation: credDef.support_revocation,
    created_at: credDef.created_at,
    created: formatDateLong(credDef.created_at),
  }));
