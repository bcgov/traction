<template>
    <div v-if="presentation">
        <ul>
          <li>Status: {{presentation.status}}</li>
          <li>Updated at: {{props.presentation.updated_at}}</li>
          <li>Contact Alias: {{props.presentation.contact.alias}}</li>
          <hr/>
            <li v-for="value, attr in props.presentation.acapy.presentation_exchange.presentation?.requested_proof.revealed_attr_groups">
              <h4>{{attr}}:</h4>
              <span v-for="val, attr_name in value.values" class="presentation-attr-value">
                <b>{{attr_name}}</b> : {{val.raw}}
                <br/>
              </span>
          </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
const props = defineProps(['presentation']);
</script>


<style>
.presentation-attr-value{
  padding-left: 1em;
}
</style>

