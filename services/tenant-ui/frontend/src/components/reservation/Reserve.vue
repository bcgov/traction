<template>
  <!-- Request successful -->
  <div v-if="reservationIdResult">
    <div v-if="loading" class="flex flex-column align-items-center">
      <ProgressSpinner />
      <p>{{ $t('reservations.loadingCheckIn') }}</p>
    </div>
    <div v-else>
      <!-- If auto-approve on, the confirmation will come right up -->
      <ShowWallet v-if="status === RESERVATION_STATUSES.SHOW_WALLET" />
      <ReservationConfirmation
        v-else
        :id="reservationIdResult"
        :email="formFields.contact_email"
        :pwd="reservationPwdResult"
      />
    </div>
  </div>

  <!-- Submit Request -->
  <div v-else>
    <form @change="myChange">
      <json-forms
        :schema="formDataSchema"
        :uischema="formUISchema"
        :renderers="renderers"
        :data="data"
        :validation-mode="formValidationMode"
        @change="onChange"
      ></json-forms>
      <Button
        type="button"
        class="w-full mt-5"
        :label="$t('common.submit')"
        :disabled="!!loading"
        :loading="!!loading"
        @click="handleSubmit(data)"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
//Vue
import { ref } from 'vue';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'vue-toastification';
import { JsonForms, JsonFormsChangeEvent } from '@jsonforms/vue';
import { vanillaRenderers } from '@jsonforms/vue-vanilla';
// State
import { useReservationStore } from '@/store';
import { storeToRefs } from 'pinia';
// Components
import { RESERVATION_STATUSES } from '@/helpers/constants';
import ShowWallet from './status/ShowWallet.vue';
import ReservationConfirmation from './ReservationConfirmation.vue';
import axios from 'axios';

const toast = useToast();

// State setup
const reservationStore = useReservationStore();
const { loading, status } = storeToRefs(useReservationStore());

// The reservation return object
const reservationIdResult: any = ref('');
const reservationPwdResult: any = ref('');

// This stores the form data.
const data: any = ref({});
const formFields: any = ref({});

// Possible values of validationMode are:
//   ValidateAndShow, ValidateAndHide, NoValidation
const formValidationMode: any = ref('ValidateAndHide');

// Store additional error messages
let formErrorMessage: any = '';

// Regex for email address
const email = /.*@.*\..+/;

/**
 * A separate change handler because jsonforms is being difficult.
 * If this is a required field, then highlight it.
 * @param event Native form event
 */
const myChange = (event: any) => {
  const value = event.target.value; // Value of element
  const required = formDataSchema.value.required; // Required fields
  const name = event.target.id.match(/.*\/properties\/(.*)-.*/)[1];

  // If a required field and it's empty, highlight it.
  if (required.includes(name) && value === '') {
    event.target.classList.add('highlight');
  } else {
    event.target.classList.remove('highlight');
  }

  // Special use case for email address
  if (name === 'emailAddress' && !value.match(email)) {
    event.target.classList.add('highlight');
  } else if (name === 'emailAddress' && value.match(email)) {
    event.target.classList.remove('highlight');
  }
};

// Make sure the data object is updated when the form changes.
const onChange = (event: JsonFormsChangeEvent) => {
  data.value = event.data;
};

/**
 * This is the form schema and UI schema.
 * It is specifically not integrated into the front end build so that it can be
 * updated separately depending on the deployment.
 */

/**
 * Create the form object by first defining the mandatory properties.
 */
const manProperties = {
  tenantName: {
    type: 'string',
  },
  emailAddress: {
    type: 'string',
  },
};

const manRequired = ['emailAddress', 'tenantName'];
const manElements = [
  {
    type: 'Control',
    scope: '#/properties/tenantName',
  },
  {
    type: 'Control',
    scope: '#/properties/emailAddress',
  },
];

const formDataSchema: any = ref({});
const formUISchema: any = ref({});

/**
 * ## compileForm
 * Compile the JSON Forms object by blending the mandatory properties
 * and schema above with any customizations from the forms/reservations.json file.
 * @param response Axios response object
 */
const compileForm = (response: any) => {
  /**
   * If there is a custom properties object,
   * then merge it with the mandatory properties.
   */
  let mergedProperties = {};
  if (response.data?.formDataSchema?.properties) {
    mergedProperties = {
      ...manProperties,
      ...response.data.formDataSchema.properties,
    };
    /**
     * Otherwise, just use the mandatory properties.
     */
  } else {
    mergedProperties = manProperties;
  }

  /**
   * If there is a custom required array,
   * then merge it with the mandatory required array.
   */
  let mergedRequired = [];
  if (response.data?.formDataSchema?.required) {
    mergedRequired = [...manRequired, ...response.data.formDataSchema.required];
    /**
     * Otherwise, just use the mandatory required array.
     */
  } else {
    mergedRequired = manRequired;
  }

  /**
   * Build the final form data schema object,
   * and save it to the formDataSchema ref.
   */
  formDataSchema.value = {
    type: 'object',
    properties: { ...mergedProperties },
    required: [...mergedRequired],
  };

  let mergedElements = [];
  if (response.data?.formUISchema?.elements) {
    mergedElements = [...manElements, ...response.data.formUISchema.elements];
  } else {
    mergedElements = manElements;
  }

  formUISchema.value = {
    type: 'VerticalLayout',
    elements: [...mergedElements],
  };
};

axios
  .get('forms/reservation.json')
  .then(compileForm)
  .catch((error) => {
    console.error('Could not find any custom form configuration. :(', error);
    console.info('Defaulting to the hard-coded form configuration.');

    formDataSchema.value = {
      type: 'object',
      properties: { ...manProperties },
      required: [...manRequired],
    };
    formUISchema.value = {
      type: 'VerticalLayout',
      elements: [...manElements],
    };
  });

const renderers = [...vanillaRenderers];

/**
 * Check if the form is valid.
 * @returns {boolean} True if the form is valid, false otherwise.
 */
const formIsValid = () => {
  const schema = formDataSchema.value;
  const fields = Object.keys(data.value);

  console.log('data', data.value);

  // If there is an email address, make sure it is valid.
  if (data.value.emailAddress && !data.value.emailAddress.match(email)) {
    // Provide a more specific error message
    formErrorMessage = 'Please enter a valid email address.';
    return false;
  } else if (
    // Clear error message if it was set before. Then allow for other checks.
    !data.value.emailAddress ||
    data.value.emailAddress.match(email)
  ) {
    formErrorMessage = '';
  }

  // If there are no required fields, then the form is valid.
  if (!('required' in schema) || schema.required?.length < 1) {
    return true;

    /**
     * If there are entries in the required array,
     * then check if they are all in the form.
     * .... and they're not undefined 💣 ... This one got me good.
     */
  } else if (
    schema.required.every(
      (field: string) =>
        fields.includes(field) &&
        data.value[field] &&
        data.value[field] !== undefined
    )
  ) {
    return true;

    // Otherwise, the form is not valid.
  } else {
    return false;
  }
};

/**
 * Submit the form
 * @param event
 * Send the reservation form data to the API. But only
 * if the form is valid.
 */
const handleSubmit = async (event: any) => {
  // Show messages for the build in validator
  formValidationMode.value = 'ValidateAndShow';

  if (!formIsValid())
    return toast.error(`Missing required fields. ${formErrorMessage}`);

  try {
    // Destructure and rebuild data object for the API
    const { emailAddress, tenantName, ...contextData } = data.value;
    formFields.value = {
      contact_email: emailAddress,
      tenant_name: tenantName,
      context_data: contextData,
    };

    const res = await reservationStore.makeReservation(formFields.value);
    reservationIdResult.value = res.reservation_id;
    reservationPwdResult.value = res.reservation_pwd
      ? res.reservation_pwd
      : undefined;
  } catch (err) {
    console.error(err);
    toast.error(`Failure making request: ${err}`);
  }
};
</script>
<style scoped lang="scss">
:deep(.control) {
  margin-bottom: 0.5rem;
  input,
  textarea {
    width: 100%;
    border-radius: 5px;
    border: 1px solid #ced4da;
    padding: 0.45rem;
    color: #495057;
    font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
    font-size: 1rem;
  }
  input:hover,
  input:focus,
  textarea:hover,
  textarea:focus {
    border-color: #2b3f51;
  }
  input:focus,
  textarea:focus {
    box-shadow: 0 0 0.3rem 0.1rem #87a6c1;
  }
  input:focus-visible,
  textarea:focus-visible {
    outline: none;
  }
  .error {
    font-weight: 200;
    color: red;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }
  input.highlight {
    border-color: red;
  }
}
:deep(.vertical-layout-item) {
  margin: 1.5rem 0 1rem 0;
}
</style>
