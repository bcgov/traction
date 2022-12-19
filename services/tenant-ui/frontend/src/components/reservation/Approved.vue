<template>
  <div class="container">
    <div class="header">
      <div class="symbol">
        <svg
          class="w-6 h-6"
          data-darkreader-inline-stroke=""
          fill="none"
          stroke="currentColor"
          style="--darkreader-inline-stroke: currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
          ></path>
        </svg>
      </div>
      <div class="message">approved!</div>
    </div>
    <div class="content">
      <p>
        We have sent a reservation password to your email address on
        {{ sentAt }}.
      </p>
      <p>
        Please enter the reservation password below to validate your account.
      </p>
      <Password
        v-model="password"
        toggleMask
        :feedback="false"
        placeholder="Password"
      />
      <Button label="Validate" @click="submit" />
      <p>
        The reservation password is only valid for 48 hours from the time it was
        sent to your email address. <br />
        Please <a href="/contact">click here</a> to request a new reservation
        password.
      </p>
    </div>
    <div class="footer">
      <hr />
      (Please check your junk/spam folder before contacting us, as it is very
      common to have the email delivery problems because of automated filters.)
    </div>
  </div>
</template>

<script setup lang="ts">
import Password from 'primevue/password';
import Button from 'primevue/button';
import { ref } from 'vue';
import { useTenantApi } from '@/store/tenantApi';
import { API_PATH } from '@/helpers/constants';
import { useToast } from 'vue-toastification';
const sentAt = 'fake date';
const password = ref('');
const tenantApi = useTenantApi();
const api = API_PATH.MULTITENANCY_RESERVATION;
const toast = useToast();

const submit = async () => {
  const url = `${api}/${props.reservationId}/check-in`;
  await tenantApi
    .postHttp(url, {
      reservation_pwd: password.value,
    })
    .then((response) => {
      // TBD: redirect to the tenant's home page
      toast.success(response.message);
    })
    .catch((error) => {
      toast.error(error.message);
    });
};

/**
 * Accepts the following props:
 */
const props = defineProps({
  email: String,
  reservationId: String,
});
</script>

<style scoped>
.container {
  display: grid;
  grid-template-rows: 90px 1fr 80px;
  grid-template-columns: 1fr;
  grid-template-areas:
    'header'
    'content'
    'footer';
  background-color: #d6deec;
  margin-top: 2rem;
  border-radius: 5px;
  border-style: solid;
  border-width: 4px;
  border-color: rgba(43, 54, 81, 0.1);
}
.header {
  grid-area: header;
  align-items: center;
  text-align: center;
  color: #2b3651;
  font-size: 1.6rem;
  font-weight: 800;
  padding: 1rem;
}
.header .message {
  text-transform: uppercase;
}
.header .symbol svg {
  stroke: #2b3651;
  height: 50px;
}
.content,
.footer {
  padding: 0 1.5rem;
}
.footer {
  font-weight: bolder;
  font-size: 0.9rem;
  line-height: normal;
}
:deep(.p-password),
:deep(input) {
  width: 100%;
}
button {
  width: 100%;
  margin-top: 1rem;
}
</style>
