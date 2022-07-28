<script setup lang="ts">
import { ref, inject } from "vue";
import Button from "primevue/button";
import axios from "axios";

/**
 * ##callBackend
 * Check a call to the tenantUI backend
 */
const callBackend = () => {

  axios({
    method: "get",
    url: "/api/hello"
  })
    .then((res) => {
      alert(JSON.stringify(res.data));
    });
};

/**
 * ##callTraction
 * Check a call to the tenantUI backend
 */
const callTraction = () => {

  axios({
    method: "get",
    url: "/api/traction"
  })
    .then((res) => {
      alert(JSON.stringify(res.data));
    });
};
</script>

<template>
  <h2>Call the Tenant UI backend and Traction API</h2>
  <Button label="Call Backend API" @click="callBackend"></Button> 
  <br /> <br />
  <Button label="Call Traction API" @click="callTraction"></Button>
</template>
