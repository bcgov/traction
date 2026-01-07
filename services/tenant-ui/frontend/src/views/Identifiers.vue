<template>
  <MainCardContent
    :title="$t('identifiers.identifiers')"
    :refresh-callback="refreshWebvh"
  >
    <div v-if="pageLoading" class="flex justify-content-center">
      <ProgressSpinner />
    </div>
    <template v-else>
      <Message
        v-if="needsWebvhConfig"
        severity="warn"
        :closable="false"
        class="config-warning"
      >
        <div class="config-warning-content">
          <p class="mb-2">
            {{ $t('identifiers.webvh.configureDescription') }}
          </p>
          <div class="config-actions">
            <Button
              type="button"
              icon="pi pi-cog"
              class="p-button-sm"
              :label="$t('identifiers.webvh.configureButton')"
              :disabled="!canConfigureWebvh || configuringWebvh"
              :loading="configuringWebvh"
              @click="configureWebvh()"
            />
            <span v-if="!canConfigureWebvh" class="text-muted">
              {{ $t('identifiers.webvh.configureMissingUrl') }}
            </span>
          </div>
        </div>
      </Message>
      <DataTable
        v-model:filters="didTableFilters"
        :value="sortedDidRows"
        :paginator="true"
        :rows="TABLE_OPT.ROWS_DEFAULT"
        :rows-per-page-options="TABLE_OPT.ROWS_OPTIONS"
        :global-filter-fields="[
          'ledger',
          'alias',
          'namespace',
          'did',
          'status',
          'type',
        ]"
        data-key="did"
        size="small"
        striped-rows
        :loading="refreshingWebvh || !webvhConfigLoaded"
        removable-sort
        :row-class="rowClass"
        @sort="onSort"
      >
        <template #header>
          <div class="table-header">
            <div class="left">
              <Button
                type="button"
                icon="pi pi-plus"
                :label="$t('identifiers.webvh.createButton')"
                class="p-button"
                :disabled="!webvhConfigLoaded || needsWebvhConfig"
                @click="openCreateDialog"
              />
            </div>
            <IconField icon-position="left" class="search-field">
              <InputIcon><i class="pi pi-search" /></InputIcon>
              <InputText
                v-model="didTableFilters.global.value"
                :placeholder="$t('identifiers.webvh.searchPlaceholder')"
              />
            </IconField>
          </div>
        </template>
        <template #empty>{{ $t('common.noRecordsFound') }}</template>
        <template #loading>{{ $t('common.loading') }}</template>
        <Column
          field="ledger"
          :header="$t('identifiers.webvh.ledger')"
          sortable
        />
        <Column
          field="alias"
          :header="$t('identifiers.webvh.alias')"
          sortable
        />
        <Column
          field="namespace"
          :header="$t('identifiers.webvh.namespace')"
          sortable
        />
        <Column
          field="status"
          :header="$t('identifiers.webvh.statusHeader')"
          sortable
        >
          <template #body="{ data }">
            <span :class="['status-chip', data.status]">
              {{ statusLabel(data.status) }}
            </span>
          </template>
        </Column>
        <Column field="did" :header="$t('identifiers.webvh.didHeader')">
          <template #body="{ data }">
            <code>{{ data.did }}</code>
          </template>
        </Column>
      </DataTable>

      <Dialog
        v-model:visible="showCreateDidDialog"
        modal
        :header="$t('identifiers.webvh.createDialogTitle')"
        :style="{ width: '32rem' }"
        @hide="resetCreateForm"
      >
        <div class="dialog-content">
          <div class="field">
            <label for="server-select">
              {{ $t('identifiers.webvh.serverUrl') }}
            </label>
            <Dropdown
              id="server-select"
              v-model="selectedWebvhServer"
              :options="availableWebvhServers"
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="!availableWebvhServers.length"
            />
            <small v-if="!availableWebvhServers.length" class="p-error">
              {{ $t('identifiers.webvh.serverUrlMissing') }}
            </small>
          </div>
          <div class="field">
            <label for="dialog-namespace" class="required-label">
              {{ $t('identifiers.webvh.namespace') }}
            </label>
            <InputText
              id="dialog-namespace"
              v-model.trim="newDidNamespace"
              autocomplete="off"
              :class="{ 'p-invalid': createFormTouched && !newDidNamespace }"
            />
            <small v-if="createFormTouched && !newDidNamespace" class="p-error">
              {{ $t('identifiers.webvh.namespaceRequired') }}
            </small>
          </div>
          <div class="field">
            <label for="dialog-alias" class="required-label">
              {{ $t('identifiers.webvh.alias') }}
            </label>
            <InputText
              id="dialog-alias"
              v-model.trim="newDidAlias"
              autocomplete="off"
              :class="{ 'p-invalid': createFormTouched && !newDidAlias }"
            />
            <small v-if="createFormTouched && !newDidAlias" class="p-error">
              {{ $t('identifiers.webvh.aliasRequired') }}
            </small>
          </div>

          <!-- DID Preview -->
          <div v-if="didPreview" class="field">
            <label class="font-semibold">{{
              $t('identifiers.webvh.didPreview')
            }}</label>
            <div class="p-3 surface-100 border-round mt-2">
              <!-- eslint-disable-next-line vue/no-v-html -->
              <code class="text-sm" v-html="didPreviewFormatted"></code>
            </div>
          </div>
        </div>
        <template #footer>
          <Button
            type="button"
            class="p-button-text"
            :disabled="creatingDid"
            :label="$t('common.cancel')"
            @click="closeCreateDialog"
          />
          <Button
            type="button"
            icon="pi pi-plus"
            :disabled="!canCreateDid"
            :loading="creatingDid"
            :label="$t('identifiers.webvh.createButton')"
            @click="submitCreateDid"
          />
        </template>
      </Dialog>
    </template>
  </MainCardContent>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from 'vue';
import type { ServerConfig } from '@/types';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import ProgressSpinner from 'primevue/progressspinner';
import Dialog from 'primevue/dialog';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
import MainCardContent from '@/components/layout/mainCard/MainCardContent.vue';
import { useTenantStore } from '@/store';
import { storeToRefs } from 'pinia';
import { useAcapyApi } from '@/store/acapyApi';
import { API_PATH, TABLE_OPT } from '@/helpers/constants';
import Message from 'primevue/message';

const toast = useToast();
const { t } = useI18n();
const tenantStore = useTenantStore();
const acapyApi = useAcapyApi();
const {
  tenantWallet,
  loading,
  serverConfig,
  webvhConfig: tenantWebvhConfig,
  walletDids,
  publicDid,
  writeLedger,
} = storeToRefs(tenantStore);
const creatingDid = ref(false);
const refreshingWebvh = ref(false);
const showCreateDidDialog = ref(false);
const createFormTouched = ref(false);
const newDidAlias = ref('');
const newDidNamespace = ref('default');
const selectedWebvhServer = ref<string | null>(null);
const webvhConfigLoaded = ref(false);
const didTableFilters = ref({
  global: { value: '', matchMode: FilterMatchMode.CONTAINS },
});
const configuringWebvh = ref(false);

const serverConfigValue = computed<ServerConfig | null>(() => {
  const value = serverConfig.value as ServerConfig | undefined;
  return value && 'config' in value ? value : null;
});

const serverWebvhConfig = computed(() => {
  const pluginConfig = serverConfigValue.value?.config?.plugin_config;
  if (!pluginConfig) {
    return null;
  }
  const keyedConfig = pluginConfig as typeof pluginConfig & Record<string, any>;
  return keyedConfig.webvh ?? keyedConfig['did-webvh'] ?? null;
});

const availableWebvhServers = computed(() => {
  if (!serverWebvhConfig.value?.server_url) {
    return [] as Array<{ label: string; value: string }>;
  }
  let label = serverWebvhConfig.value.server_url;
  try {
    const parsed = new URL(serverWebvhConfig.value.server_url);
    label = parsed.hostname;
  } catch (_error) {
    // leave label as raw server_url
  }
  return [
    {
      label,
      value: serverWebvhConfig.value.server_url,
    },
  ];
});

watchEffect(() => {
  if (!selectedWebvhServer.value && availableWebvhServers.value.length) {
    selectedWebvhServer.value = availableWebvhServers.value[0].value;
  }
});

const pageLoading = computed(() => {
  if (loading.value) {
    return true;
  }
  // Don't wait for tenantWebvhConfig to be truthy - it may be null/empty if not configured
  if (webvhConfigLoaded.value && 'config' in (serverConfig.value ?? {})) {
    return false;
  }
  return true;
});

const webvhConfig = computed<any | null>(() => {
  const tenantConfig = tenantWebvhConfig.value;
  const base = serverWebvhConfig.value;
  if (!tenantConfig || Object.keys(tenantConfig).length === 0) {
    return base ?? tenantConfig ?? null;
  }
  if (!base) {
    return tenantConfig;
  }
  return {
    ...base,
    ...tenantConfig,
  };
});

const webvhWitnesses = computed(() => {
  if (!webvhConfig.value) return [] as string[];
  const witnesses = webvhConfig.value.witnesses;
  if (Array.isArray(witnesses) && witnesses.length) {
    return witnesses;
  }
  return [] as string[];
});

const webvhWatchers = computed(() => {
  if (!webvhConfig.value) return [] as string[];
  const watchers = webvhConfig.value.watchers;
  if (Array.isArray(watchers) && watchers.length) {
    return watchers;
  }
  return [] as string[];
});

const hasWebvhConfig = computed(() => {
  const cfg = webvhConfig.value;
  if (!cfg) {
    return false;
  }
  const witnesses = cfg.witnesses ?? cfg.watchers;
  const hasWitnesses = Array.isArray(witnesses) && witnesses.length > 0;
  return Boolean(cfg.server_url && hasWitnesses);
});

const canConfigureWebvh = computed(() => {
  return Boolean(serverWebvhConfig.value?.server_url);
});

const needsWebvhConfig = computed(() => !hasWebvhConfig.value);

const webvhDidRows = computed(() => {
  const rows: Array<{
    scid?: string;
    did: string;
    alias: string;
    namespace: string;
    ledger: string;
    status: string;
    type: 'indy' | 'webvh';
    isPublicIndy?: boolean;
  }> = [];

  // Add public Indy DID as first entry (sticky)
  const indyPublicDid = publicDid.value?.did;
  if (indyPublicDid) {
    rows.push({
      did: indyPublicDid,
      alias: 'Public Indy DID',
      namespace: '-',
      ledger: writeLedger.value?.ledger_id || '-',
      status: 'active',
      type: 'indy',
      isPublicIndy: true,
    });
  }

  // Add WebVH DIDs from walletDids
  const allDids = walletDids.value || [];
  allDids.forEach((didRecord: any) => {
    const { did, method, posture } = didRecord;

    // Filter for WebVH DIDs only
    if (method === 'webvh') {
      // Parse WebVH DID to extract domain, namespace, alias
      // Format: did:webvh:{SCID}:domain:namespace:alias
      const segments = did.split(':');
      const alias = segments[segments.length - 1] || did;
      const namespace =
        segments.length > 4 ? segments[segments.length - 2] : 'default';
      const ledger = segments.length >= 6 ? segments[3] : '';

      // Extract SCID (3rd segment after did:webvh:)
      const scid = segments.length > 2 ? segments[2] : undefined;

      rows.push({
        scid,
        did,
        alias,
        namespace,
        ledger,
        status: posture === 'public' ? 'active' : posture,
        type: 'webvh',
        isPublicIndy: false,
      });
    }
  });

  return rows;
});

const statusLabel = (_status: string) =>
  t('identifiers.webvh.statusActive') as string;

const rowClass = (data: any) => {
  if (data.isPublicIndy) {
    return 'public-indy-did-row';
  }
  return '';
};

// Custom sort function to keep Indy public DID always first
const sortedDidRows = ref<typeof webvhDidRows.value>([]);

watchEffect(() => {
  sortedDidRows.value = webvhDidRows.value;
});

const onSort = (event: any) => {
  const { sortField, sortOrder } = event;

  if (!sortField) {
    sortedDidRows.value = webvhDidRows.value;
    return;
  }

  const rows = [...webvhDidRows.value];
  const indyRow = rows.find((r) => r.isPublicIndy);
  const otherRows = rows.filter((r) => !r.isPublicIndy);

  // Sort the non-Indy rows
  otherRows.sort((a: any, b: any) => {
    const aVal = a[sortField];
    const bVal = b[sortField];

    if (aVal === bVal) return 0;
    if (aVal < bVal) return sortOrder === 1 ? -1 : 1;
    return sortOrder === 1 ? 1 : -1;
  });

  // Always put Indy row first
  sortedDidRows.value = indyRow ? [indyRow, ...otherRows] : otherRows;
};

const canCreateDid = computed(
  () =>
    !needsWebvhConfig.value &&
    selectedWebvhServer.value &&
    newDidNamespace.value.trim().length > 0 &&
    newDidAlias.value.trim().length > 0 &&
    !creatingDid.value
);

// Computed property for DID preview
const didPreview = computed(() => {
  const namespace = newDidNamespace.value.trim() || '{namespace}';
  const alias = newDidAlias.value.trim() || '{alias}';
  const server = selectedWebvhServer.value;

  if (!server) {
    return '';
  }

  // Extract domain from server URL
  let domain = '';
  try {
    const url = new URL(server);
    domain = url.hostname;
  } catch {
    // If server is not a valid URL, use it as-is
    domain = server.replace(/^https?:\/\//, '').split('/')[0];
  }

  return `did:webvh:{SCID}:${domain}:${namespace}:${alias}`;
});

// Formatted DID preview with bold namespace and alias
const didPreviewFormatted = computed(() => {
  const namespace = newDidNamespace.value.trim() || '{namespace}';
  const alias = newDidAlias.value.trim() || '{alias}';
  const server = selectedWebvhServer.value;

  if (!server) {
    return '';
  }

  // Extract domain from server URL
  let domain = '';
  try {
    const url = new URL(server);
    domain = url.hostname;
  } catch {
    // If server is not a valid URL, use it as-is
    domain = server.replace(/^https?:\/\//, '').split('/')[0];
  }

  return `did:webvh:{SCID}:${domain}:<strong>${namespace}</strong>:<strong>${alias}</strong>`;
});

const openCreateDialog = () => {
  createFormTouched.value = false;
  showCreateDidDialog.value = true;
};

const closeCreateDialog = () => {
  showCreateDidDialog.value = false;
};

const resetCreateForm = () => {
  newDidAlias.value = '';
  newDidNamespace.value = 'default';
  createFormTouched.value = false;
};

const submitCreateDid = async () => {
  createFormTouched.value = true;
  if (!newDidNamespace.value.trim() || !newDidAlias.value.trim()) {
    return;
  }
  await createDid();
};

const loadWebvhConfig = async () => {
  await tenantStore.getWebvhConfig();
  webvhConfigLoaded.value = true;
};

const configureWebvh = async (auto = false) => {
  if (!auto) {
    configuringWebvh.value = true;
  }
  try {
    const result = await tenantStore.configureWebvhPlugin({ auto });
    if (!result.success) {
      if (!auto && 'reason' in result) {
        const failureMessage =
          result.reason === 'missing_witness_id'
            ? t('identifiers.webvh.witnessMissing')
            : result.reason === 'missing_server_url'
              ? t('identifiers.webvh.configureMissingUrl')
              : t('identifiers.webvh.autoConfigureFailed');
        toast.error(failureMessage as string);
      }
      return false;
    }
    if (!auto) {
      toast.success(t('identifiers.webvh.configureSuccess') as string);
      await loadWebvhConfig();
    }
    return true;
  } catch (error: any) {
    if (!auto) {
      toast.error(
        `Failed to configure webvh: ${
          error?.response?.data?.message ?? JSON.stringify(error ?? {})
        }`
      );
    }
    return false;
  } finally {
    if (!auto) {
      configuringWebvh.value = false;
    }
  }
};

const refreshWebvh = async () => {
  if (refreshingWebvh.value) {
    return;
  }
  refreshingWebvh.value = true;
  try {
    await tenantStore.getServerConfig();
    await tenantStore.getWalletDids();
    await tenantStore.getPublicDid();
    await tenantStore.getWriteLedger();
    await loadWebvhConfig();
  } finally {
    refreshingWebvh.value = false;
  }
};

const createDid = async () => {
  creatingDid.value = true;
  try {
    if (needsWebvhConfig.value || !selectedWebvhServer.value) {
      toast.error(t('identifiers.webvh.serverUrlMissing') as string);
      return;
    }
    const namespace = newDidNamespace.value.trim();
    const alias = newDidAlias.value.trim();

    const options: Record<string, any> = {
      identifier: alias,
      namespace,
      server_url: selectedWebvhServer.value,
    };
    // Set witnesses if configured
    if (webvhWitnesses.value.length) {
      options.witnesses = webvhWitnesses.value;
      // Set witness threshold
      options.witness = { threshold: 1 };
    }

    // Set watchers if configured (separate from witnesses)
    if (webvhWatchers.value.length) {
      options.watchers = webvhWatchers.value;
    }

    const response = await acapyApi.postHttp(API_PATH.DID_WEBVH_CREATE, {
      options,
    });

    const newDid = response?.data?.did ?? response?.data?.did_document?.id;
    toast.success(
      newDid
        ? t('identifiers.webvh.createSuccessWithDid', { did: newDid })
        : t('identifiers.webvh.createSuccess')
    );
    resetCreateForm();
    showCreateDidDialog.value = false;
    await tenantStore.getServerConfig();
    await loadWebvhConfig();
  } catch (error: any) {
    toast.error(
      `Failed to create DID: ${
        error?.response?.data?.message ??
        JSON.stringify(error?.response?.data ?? error)
      }`
    );
  } finally {
    creatingDid.value = false;
  }
};

onMounted(async () => {
  const tasks: Promise<any>[] = [];
  if (!tenantWallet.value) {
    tasks.push(tenantStore.getTenantSubWallet());
  }
  if (!('config' in (serverConfig.value ?? {}))) {
    tasks.push(tenantStore.getServerConfig());
  }
  // Fetch wallet DIDs, public DID, and write ledger for Indy identifier display
  tasks.push(tenantStore.getWalletcDids());
  tasks.push(tenantStore.getPublicDid());
  tasks.push(tenantStore.getWriteLedger());

  if (tasks.length) {
    await Promise.allSettled(tasks);
  }
  await loadWebvhConfig();
});
</script>

<style scoped lang="scss">
.wallet-type-check {
  padding: 1rem 0;
}

.webvh-section {
  display: flex;
  flex-direction: column;
}

.webvh-row {
  display: flex;
  margin-bottom: 0.75rem;

  .label {
    min-width: 9rem;
    font-weight: 600;
  }

  .value {
    flex: 1;
    word-break: break-word;
  }

  .icon {
    display: inline-flex;
    align-items: center;
  }
}

.create-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;

  .field {
    min-width: 14rem;
  }
}

.status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  line-height: 1;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  background-color: rgba(3, 155, 229, 0.12);
  color: rgba(3, 155, 229, 1);
}

.config-warning {
  margin-bottom: 1rem;
}

.config-warning-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.config-warning-error {
  color: $tenant-ui-text-danger;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;

  .left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .search-field {
    flex: 1;
    max-width: 18rem;
  }
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.required-label::after {
  content: ' *';
  color: $tenant-ui-text-danger;
}

:deep(.public-indy-did-row) {
  background-color: rgba(59, 130, 246, 0.08) !important;
  font-weight: 500;
  border-left: 3px solid rgba(59, 130, 246, 0.6);

  &:hover {
    background-color: rgba(59, 130, 246, 0.12) !important;
  }

  td {
    font-weight: 500;
  }
}
</style>
