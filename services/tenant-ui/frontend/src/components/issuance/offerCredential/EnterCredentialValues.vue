<template>
  <Button
    icon="pi pi-arrow-left"
    class="p-button-rounded p-button-text mr-2 pt-3"
    @click="$emit('back')"
  />
  <strong>{{ props.header }}</strong>

  <div class="field mt-5">
    <!-- Label/toggle -->
    <div class="flex justify-content-between">
      <div class="flex justify-content-start">
        <label for="credentialValuesEdit">
          <strong>Credential Field Values</strong>
        </label>
      </div>
      <div class="flex justify-content-end">
        JSON
        <InputSwitch v-model="showRawJson" class="ml-1" @input="toggleJson" />
      </div>
    </div>

    <!-- Raw JSON input mode -->
    <div v-show="showRawJson">
      <Textarea
        id="credentialValuesEdit"
        v-model="credentialValuesJson"
        :auto-resize="true"
        rows="20"
        cols="60"
        class="w-full mt-1"
      />

      <div class="flex justify-content-end">
        <small>
          Schema: {{ schemaForSelectedCred.schema_name }} Version:
          {{ schemaForSelectedCred.version }}
        </small>
      </div>
    </div>

    <!-- Dynamic Attribute field list -->
    <div v-show="!showRawJson">
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
    </div>

    <Button label="Save" class="mt-5 w-full" @click="saveCredValues" />
  </div>
</template>

<script setup lang="ts">
// Vue
import { onMounted, ref } from 'vue';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputSwitch from 'primevue/inputswitch';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import { useToast } from 'vue-toastification';

const toast = useToast();

// Props
interface Props {
  existingCredentialValues?: { name: string; value: string }[];
  header: String;
  schemaForSelectedCred: any;
}
const props = defineProps<Props>();

const emit = defineEmits(['back', 'save']);

// Fields
const credentialValuesJson = ref('');
const credentialValuesRaw = ref([] as { name: string; value: string }[]);

const showRawJson = ref(false);

// TODO: util function file
function _tryParseJson(jsonString: string) {
  try {
    const o = JSON.parse(jsonString);
    if (o && typeof o === 'object') {
      return o;
    }
    return false;
  } catch (e) {
    return false;
  }
}

function _jsonToCredRaw() {
  const parsed = _tryParseJson(credentialValuesJson.value);
  if (parsed) {
    credentialValuesRaw.value = JSON.parse(credentialValuesJson.value);
  } else {
    toast.warning('The JSON you inputted has invalid syntax');
  }
}

const toggleJson = () => {
  if (showRawJson.value) {
    // Convert over to the json from what was entered on the fields
    credentialValuesJson.value = JSON.stringify(
      credentialValuesRaw.value,
      undefined,
      2
    );
  } else {
    // Parse the entered JSON into fields, or ignore and warn if invalid syntax
    _jsonToCredRaw();
  }
};

const saveCredValues = () => {
  if (showRawJson.value) {
    _jsonToCredRaw();
  }
  emit('save', credentialValuesRaw.value);
};

// Whnen the component is intialized set up the fields and raw JSON based
// on the supplied schema and if there is existing values already
onMounted(() => {
  // Popuplate cred editor if it's not already been edited
  if (!props.existingCredentialValues?.length) {
    const schemaFillIn = props.schemaForSelectedCred.attributes.map(
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
  credentialValuesJson.value = JSON.stringify(
    credentialValuesRaw.value,
    undefined,
    2
  );
});
</script>
