<template>
  <div>
    <h2>Students</h2>
    <div v-if="currentSandbox">
      <!-- table header -->
      <v-data-table
        :headers="headers"
        item-key="id"
        :items="currentSandbox.students"
      >
        <template #[`item.created_at`]="{ item }">
          {{ item.created_at | formatDateLong }}
        </template>
        <template #[`item.actions`]>
          <v-btn color="primary" @click="invite">Invite</v-btn>
        </template>
      </v-data-table>
    </div>
    <div v-else>
      No sandbox session set, please go to Innkeeper tab to set that up
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Students',
  data() {
    return {
      headers: [
        { text: 'name', align: 'start', value: 'name' },
        { text: 'Id', align: 'start', value: 'id' },
        { text: 'Created', align: 'start', value: 'created_at' },
        {
          text: 'Actions',
          align: 'end',
          value: 'actions',
          filterable: false,
          sortable: false,
        },
      ],
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes', 'currentSandbox']),
  },
  methods: {
    invite() {
      alert('TBD');
    },
  },
};
</script>

<style>
</style>
