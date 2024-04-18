<template>
  <div class="flex align-content-center">
    <Button
      icon="pi pi-arrow-left"
      class="p-button-rounded p-button-text mr-2 flex align-items-center"
      @click="$emit('back')"
    />
    <div class="flex align-items-center">
      <strong>{{ props.header }}</strong>
    </div>
  </div>

  <div class="field mt-5">
    <ToggleJson
      ref="jsonVal"
      :to-json="credentialValueToJson"
      :from-json="jsonToCredentialValue"
      generic="CredentialValue[]"
    >
      <!-- Dynamic Attribute field list -->
      <div
        v-for="(item, index) in credentialValuesRaw"
        :key="item.name"
        class="field"
      >
        <label :for="item.name">
          {{ item.name }}
        </label>
        <InputText
          :id="item.name"
          v-model="credentialValuesRaw[index].value"
          class="w-full"
        />
      </div>
    </ToggleJson>
    <div class="flex justify-content-end">
      <small>
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        {{ $t('issue.schema') }}: {{ schemaForSelectedCred.schema.name }}
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        {{ $t('issue.version') }}:
        {{ schemaForSelectedCred.schema.version }}
      </small>
    </div>
    <Button label="Save" class="mt-5 w-full" @click="saveCredValues" />
  </div>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import { tryParseJson } from '@/helpers/jsonParsing';
import ToggleJson from '@/components/common/ToggleJson.vue';

const toast = useToast();

// Props
interface CredentialValue {
  name: string;
  value: string;
}
interface Props {
  existingCredentialValues?: CredentialValue[];
  header: String;
  schemaForSelectedCred: any;
}
const props = defineProps<Props>();

const emit = defineEmits(['back', 'save']);

// Fields
const credentialValuesRaw = ref<CredentialValue[]>([]);

const jsonVal = ref<{ showRawJson: boolean; valuesJson: string }>({
  showRawJson: false,
  valuesJson: '',
});

function jsonToCredentialValue(
  jsonString: string
): CredentialValue[] | undefined {
  const parsed = tryParseJson<CredentialValue[]>(jsonString);
  if (parsed) {
    credentialValuesRaw.value = parsed;
    return parsed;
  } else {
    toast.warning('This JSON is invalid syntax');
    return undefined;
  }
}

function credentialValueToJson(): string | undefined {
  // Convert over to the json from what was entered on the fields
  const j = JSON.stringify(credentialValuesRaw.value, undefined, 2);
  return j;
}

const saveCredValues = () => {
  if (jsonVal.value.showRawJson) {
    jsonToCredentialValue(jsonVal.value.valuesJson);
  }
  emit('save', credentialValuesRaw.value);
};

// When the component is initialized set up the fields and raw JSON based
// on the supplied schema and if there is existing values already
onMounted(() => {
  // Populate cred editor if it's not already been edited
  if (!props.existingCredentialValues?.length) {
    const schemaFillIn = props.schemaForSelectedCred.schema.attrNames.map(
      (a: string) => {
        return {
          name: `${a}`,
          value: '',
        };
      }
    );

    console.log(schemaFillIn);
    credentialValuesRaw.value = schemaFillIn;
  } else {
    credentialValuesRaw.value = props.existingCredentialValues;
  }
});
</script>
