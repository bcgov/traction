<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <div class="container">
      <div v-if="isCopy" style="text-align: center">
        <div class="info-box">
          {{ $t('configuration.schemas.copyMessage') }}
        </div>
        <p style="font-weight: bold">{{ selectedSchema?.schema_id }}</p>
      </div>
      <div class="mt-2">
        <ToggleJson
          ref="jsonVal"
          :to-json="schemaToJson"
          :from-json="jsonToSchema"
          generic="SchemaSendRequest"
        >
          <!-- schema name -->
          <ValidatedField
            :placeholder="isCopy ? selectedSchema?.schema?.name : ''"
            :field-name="'name'"
            :label="$t('issue.schemaName')"
            :loading="loading"
            :submitted="submitted"
            :validation="v$"
            :advanced-is-error="isError"
          />
          <!-- schema version -->
          <ValidatedField
            :placeholder="isCopy ? selectedSchema?.schema?.version : ''"
            :field-name="'version'"
            :label="$t('issue.schemaVersion')"
            :loading="loading"
            :submitted="submitted"
            :validation="v$"
            :advanced-is-error="isError"
          />
          <!-- issuer (only for askar-anoncreds wallets) -->
          <div v-if="isAskarAnoncredsWallet" class="field">
            <label for="issuer" class="block text-900 font-medium mb-2">
              {{ $t('configuration.schemas.issuer') }}
              <span class="text-red-500">{{ $t('common.required') }}</span>
            </label>
            <Dropdown
              id="issuer"
              v-model="formFields.issuer"
              :options="issuerIdentifiers"
              option-label="label"
              option-value="value"
              :placeholder="t('configuration.schemas.selectIssuer')"
              class="w-full"
              :class="{ 'p-invalid': v$.issuer.$error && submitted }"
              :loading="loadingIssuerIdentifiers"
            />
            <small v-if="v$.issuer.$error && submitted" class="p-error">
              {{ v$.issuer.required.$message }}
            </small>
          </div>
          <!-- attributes -->
          <Attributes
            ref="attributes"
            :initial-attributes="initialAttributes"
          />
        </ToggleJson>
        <Button
          type="submit"
          :label="t('configuration.schemas.create')"
          class="mt-5 w-full"
          :disabled="
            formFields.name === '' ||
            formFields.version === '' ||
            (isAskarAnoncredsWallet && formFields.issuer === '')
          "
          :loading="loading"
        />
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
// Libraries
import { useVuelidate } from '@vuelidate/core';
import { helpers, required } from '@vuelidate/validators';
import { computed, onMounted, reactive, ref } from 'vue';
import { storeToRefs } from 'pinia';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
// Source
import ValidatedField from '@/components/common/ValidatedField.vue';
import errorHandler from '@/helpers/errorHandler';
import { tryParseJson } from '@/helpers/jsonParsing';
import { useGovernanceStore, useTenantStore } from '@/store';
import { Attribute } from '@/types';
import {
  AnonCredsSchema,
  SchemaPostRequest,
  SchemaSendRequest,
} from '@/types/acapyApi/acapyInterface';
import Attributes from './Attributes.vue';
import ToggleJson from '@/components/common/ToggleJson.vue';

const toast = useToast();
const { t } = useI18n();

const governanceStore = useGovernanceStore();
const { loading, selectedSchema } = storeToRefs(useGovernanceStore());

const tenantStore = useTenantStore();
const { tenantWallet, publicDid } = storeToRefs(tenantStore);

// Check if wallet is askar-anoncreds
const isAskarAnoncredsWallet = computed(() => {
  return tenantWallet.value?.settings?.['wallet.type'] === 'askar-anoncreds';
});

// Issuer identifiers for issuer dropdown (Indy + WebVH)
const issuerIdentifiers = ref<
  Array<{ label: string; value: string; type: 'indy' | 'webvh' }>
>([]);
const loadingIssuerIdentifiers = ref(false);

const emit = defineEmits(['closed', 'success']);
const attributes = ref<{ attributes: Array<Attribute> }>({ attributes: [] });
const jsonVal = ref<{ showRawJson: boolean; valuesJson: string }>({
  showRawJson: false,
  valuesJson: '',
});
const props = defineProps({
  isCopy: {
    type: Boolean,
    required: false,
    default: false,
  },
  initialAttributes: {
    type: Array<Attribute>,
    required: false,
    default: [],
  },
  // This can be used if emit won't work from parent component
  onClose: {
    type: Function,
    required: false,
    default: () => {},
  },
});

// Form / Validation setup
const formFields = reactive({
  name: '',
  version: '',
  issuer: '',
});

const mustBeDecimal = (value: string) => /^\d+(\.\d+)(\.\d+)?$/.test(value);

const changedField = (field: string) => {
  if (field === 'name' || field === 'version')
    if (formFields[field] !== selectedSchema.value?.schema?.[field])
      return true;
  return false;
};

const isError = (v: any, field: string) => {
  if (props.isCopy)
    return v[field].$error && submitted.value && !changedField(field);
  return v[field].$error && submitted.value;
};

// Add copy rules if isCopy - need to modify rules before making it computed
let baseRulesForCopy: { [key: string]: any } = {
  name: { required },
  version: {
    required,
    mustBeDecimal: helpers.withMessage(
      t('configuration.schemas.mustBeDecimal'),
      mustBeDecimal
    ),
  },
};

if (props.isCopy) {
  const validCopy = () => {
    if (
      (changedField('name') && formFields.name !== '') ||
      (changedField('version') && formFields.version !== '')
    )
      return true;
    return false;
  };

  const setRule = (value: string | undefined, field: string) => {
    if (value)
      baseRulesForCopy[field] = {
        ...baseRulesForCopy[field],
        validCopy: helpers.withMessage(
          t('configuration.schemas.invalidCopy', {
            field,
            value,
          }),
          validCopy
        ),
      };
  };
  if (selectedSchema.value) {
    setRule(selectedSchema.value.schema?.name, 'name');
    setRule(selectedSchema.value.schema?.version, 'version');
  }

  delete baseRulesForCopy.name.required;
  delete baseRulesForCopy.version.required;
}

// Rules need to be computed to react to wallet type changes
const rules = computed(() => {
  const baseRules: { [key: string]: any } = props.isCopy
    ? { ...baseRulesForCopy }
    : {
        name: { required },
        version: {
          required,
          mustBeDecimal: helpers.withMessage(
            t('configuration.schemas.mustBeDecimal'),
            mustBeDecimal
          ),
        },
      };

  // Add issuer validation for askar-anoncreds wallets
  if (isAskarAnoncredsWallet.value) {
    baseRules.issuer = { required };
  }

  return baseRules;
});

const v$ = useVuelidate(rules, formFields);

function convertToJson(): SchemaSendRequest | SchemaPostRequest | undefined {
  const attributeNames = attributes.value?.attributes
    .filter((x: Attribute) => x.name !== '')
    .map((attribute: Attribute) => attribute.name);

  if (isAskarAnoncredsWallet.value) {
    // For askar-anoncreds wallets, use SchemaPostRequest format
    const schema: AnonCredsSchema = {
      attrNames: attributeNames ?? [],
      name: formFields.name || selectedSchema.value?.schema?.name || '',
      version:
        formFields.version || selectedSchema.value?.schema?.version || '',
      issuerId: formFields.issuer || '',
    };
    return {
      schema,
    };
  } else {
    // For askar wallets, use SchemaSendRequest format
    return {
      attributes: attributeNames ?? [],
      schema_name: formFields.name || selectedSchema.value?.schema?.name || '',
      schema_version:
        formFields.version || selectedSchema.value?.schema?.version || '',
    };
  }
}

function schemaToJson(): string | undefined {
  const rawJson: SchemaSendRequest | SchemaPostRequest | undefined =
    convertToJson();
  if (rawJson) {
    return JSON.stringify(rawJson, undefined, 2);
  } else {
    toast.error('Failed to convert to Json');
    return undefined;
  }
}

function jsonToSchema(
  jsonString: string
): SchemaSendRequest | SchemaPostRequest | undefined {
  if (isAskarAnoncredsWallet.value) {
    const parsed = tryParseJson<SchemaPostRequest>(jsonString);
    if (parsed && parsed.schema) {
      const newAt: Array<Attribute> = [
        { name: '' },
        ...parsed.schema.attrNames.map((a) => ({ name: a })),
      ];
      attributes.value.attributes = newAt;
      formFields.name = parsed.schema.name;
      formFields.version = parsed.schema.version;
      formFields.issuer = parsed.schema.issuerId;
      return parsed;
    } else {
      toast.error('Invalid JSON detected');
      return undefined;
    }
  } else {
    const parsed = tryParseJson<SchemaSendRequest>(jsonString);
    if (parsed) {
      const newAt: Array<Attribute> = [
        { name: '' },
        ...parsed.attributes.map((a) => ({ name: a })),
      ];
      attributes.value.attributes = newAt;
      formFields.name = parsed.schema_name;
      formFields.version = parsed.schema_version;
      return parsed;
    } else {
      toast.error('Invalid JSON detected');
      return undefined;
    }
  }
}
// Load issuer identifiers (Indy public DID + WebVH DIDs) for issuer dropdown
const loadIssuerIdentifiers = async () => {
  if (!isAskarAnoncredsWallet.value) {
    return;
  }

  loadingIssuerIdentifiers.value = true;
  try {
    // Fetch all DIDs from the wallet
    await tenantStore.getWalletDids();
    const allDids = tenantStore.walletDids || [];

    // Filter and format DIDs
    const identifiers: Array<{
      label: string;
      value: string;
      type: 'indy' | 'webvh';
    }> = [];

    // First, add the public Indy DID if it exists (from publicDid store)
    const indyPublicDid = publicDid.value?.did;
    if (indyPublicDid) {
      identifiers.push({
        label: 'Public Indy DID',
        value: indyPublicDid,
        type: 'indy',
      });
    }

    // Then, add DIDs from walletDids list
    allDids.forEach((didRecord: any) => {
      const { did, method, posture } = didRecord;

      // Skip if this DID is already added as the public Indy DID
      if (indyPublicDid && did === indyPublicDid) {
        return;
      }

      // Include public Indy DIDs (check by method field: 'sov' or 'indy')
      if ((method === 'sov' || method === 'indy') && posture === 'public') {
        identifiers.push({
          label: 'Public Indy DID',
          value: did,
          type: 'indy',
        });
      }
      // Include WebVH DIDs (check by method field)
      else if (method === 'webvh') {
        // Parse WebVH DID to extract domain, namespace, alias
        // Format: did:webvh:{SCID}:domain:namespace:alias
        const segments = did.split(':');
        const alias = segments[segments.length - 1] || did;
        const namespace =
          segments.length > 4 ? segments[segments.length - 2] : 'default';
        const domain = segments.length >= 6 ? segments[3] : '';

        const label = domain
          ? `${domain} : ${namespace} : ${alias}`
          : `${namespace} : ${alias}`;

        identifiers.push({
          label,
          value: did,
          type: 'webvh',
        });
      }
    });

    issuerIdentifiers.value = identifiers;
  } catch (_error) {
    console.error('Failed to load issuer identifiers:', _error);
    issuerIdentifiers.value = [];
  } finally {
    loadingIssuerIdentifiers.value = false;
  }
};

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;
  try {
    if (!isFormValid) return;

    const payload: SchemaSendRequest | SchemaPostRequest | undefined = jsonVal
      .value.showRawJson
      ? jsonToSchema(jsonVal.value.valuesJson)
      : convertToJson();

    if (!payload) return;

    // Validate attributes
    if (isAskarAnoncredsWallet.value) {
      const anoncredsPayload = payload as SchemaPostRequest;
      if (!anoncredsPayload.schema?.attrNames?.length) {
        toast.error(t('configuration.schemas.emptyAttributes'));
        return;
      }
      if (!anoncredsPayload.schema?.issuerId) {
        toast.error('Issuer is required');
        return;
      }
    } else {
      const regularPayload = payload as SchemaSendRequest;
      if (!regularPayload.attributes.length) {
        toast.error(t('configuration.schemas.emptyAttributes'));
        return;
      }
    }

    if (isAskarAnoncredsWallet.value) {
      // Use anoncreds endpoint
      await governanceStore.createAnoncredsSchema(payload as SchemaPostRequest);
    } else {
      // Use regular endpoint
      await governanceStore.createSchema(payload as SchemaSendRequest);
    }
    toast.success(t('configuration.schemas.postStart'));
    emit('success');
    emit('closed', payload);
    if (props.onClose) props.onClose(payload);
  } catch (error) {
    errorHandler({
      error,
      existsMessage: t('configuration.schemas.alreadyExists'),
    });
  } finally {
    submitted.value = false;
  }
};

onMounted(async () => {
  if (isAskarAnoncredsWallet.value) {
    // Ensure public DID is loaded before loading identifiers
    if (!publicDid.value) {
      await tenantStore.getPublicDid();
    }
    await tenantStore.getWalletcDids();
    loadIssuerIdentifiers();
  }
});
</script>

<style scoped>
.container {
  min-width: 450px;
  display: inline-block;
  text-align: left;
}
form {
  display: block;
  text-align: center;
}
.info-box {
  background-color: #eff6ff;
  border-radius: 5px;
  padding: 10px;
  margin-bottom: 10px;
}
</style>
