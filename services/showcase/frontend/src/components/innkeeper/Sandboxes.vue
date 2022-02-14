<template>
  <div>
    <h2>Current Sandbox sessions available</h2>
    <v-skeleton-loader :loading="loading" type="article">
      <p v-if="!sandboxes || !sandboxes.length">
        There are no Sandboxes currently available
      </p>
      <!-- table header -->
      <v-data-table :headers="headers" item-key="id" :items="sandboxes">
        <template #[`item.created_at`]="{ item }">
          {{ item.created_at | formatDateLong }}
        </template>
        <template #[`item.actions`]="{ item }">
          <v-btn color="primary" @click="SET_CURRENT(item)">Use</v-btn>
        </template>
      </v-data-table>
    </v-skeleton-loader>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex';

export default {
  name: 'Sandboxes',
  data() {
    return {
      headers: [
        { text: 'Tag', align: 'start', value: 'tag' },
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
      loading: true,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes', 'currentSandbox']),
  },
  methods: {
    ...mapActions('sandbox', ['getSandboxes']),
    ...mapMutations ('sandbox', ['SET_CURRENT']),
  },
  async mounted() {
    await this.getSandboxes();
    this.loading = false;
  },
};
</script>

<style>
</style>
