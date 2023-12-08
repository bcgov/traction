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
    toast.error(
      'Incorrect tenant name. Please confirm the correct name before deletion.'
    );
    return;
  }
  innkeeperTenantsStore
    .deleteTenant(props.tenant.tenant_id)
    .catch((err: string) => {
      console.log(err);
      toast.error('Failure: ${err}');
    });

  emit('success');
  emit('closed');
}
</script>
