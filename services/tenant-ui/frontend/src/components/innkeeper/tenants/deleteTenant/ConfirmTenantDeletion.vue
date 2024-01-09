<template>
  <form @submit.prevent="handleDelete">
    <div class="modal-content">
      <h4>
        {{
          $t('tenants.settings.confirmDeletion', {
            tenantName: tenant.tenant_name,
          })
        }}
      </h4>
      <InputText
        v-model.trim="confirmationTenantName"
        type="text"
        placeholder="Type the tenant name here"
        class="w-full mb-4"
      />
      <Button
        :disabled="!isTenantNameCorrect"
        label="Delete"
        severity="danger"
        class="w-full"
        type="submit"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

import { useInnkeeperTenantsStore } from '@/store';
import { TenantRecord } from '@/types/acapyApi/acapyInterface';

import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';
const { t } = useI18n();

const props = defineProps<{
  tenant: TenantRecord;
}>();

const emit = defineEmits(['closed', 'success']);

// Using stores
const innkeeperTenantsStore = useInnkeeperTenantsStore();

const confirmationTenantName = ref('');
const isTenantNameCorrect = computed(
  () => confirmationTenantName.value === props.tenant.tenant_name
);

const toast = useToast();

async function handleDelete() {
  if (!isTenantNameCorrect.value) {
    toast.error(t('tenants.settings.confirmDeletionIncorrect'));
    return;
  }
  try {
    await innkeeperTenantsStore.deleteTenant(props.tenant.tenant_id);
    toast.success(
      t('tenants.settings.confirmDeletionSuccess', [props.tenant.tenant_name])
    );
    emit('success');
    emit('closed');
  } catch (err: any) {
    console.error(err);
    toast.error('Failure: ${err}');
  }
}
</script>
