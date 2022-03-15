<template>
  <div>
    <h2>Current Sandbox sessions available</h2>
    <v-skeleton-loader :loading="loading" type="article">
      <div v-if="!sandboxes || !sandboxes.length">
        <p>There are no Sandboxes currently available</p>
      </div>
      <div v-else>
        <!-- table header -->
        <v-data-table
          :headers="headers"
          item-key="id"
          :items="sandboxes"
          show-expand
        >
          <template #[`item.created_at`]="{ item }">
            {{ item.created_at | formatDateLong }}
          </template>
          <template #[`item.actions`]="{ item }">
            <v-btn small color="primary" @click="selectSandbox(item.id)">
              Use
            </v-btn>
          </template>
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length">
              <h3>Businesses in this sandbox</h3>
              <v-row>
                <v-col v-for="lob in item.lobs" :key="lob.id">
                  <p>
                    <strong>{{ lob.name }}</strong> <br />
                    ID: {{ lob.id }} <br />
                    Wallet ID: {{ lob.wallet_id }} <br />
                    Wallet Key: {{ lob.wallet_key }} <br />
                    Traction Issue Enabled: {{ lob.traction_issue_enabled }} <br />
                    Public DID: {{ lob.public_did }} <br />
                    Cred. Def ID: {{ lob.cred_def_id }}
                    <br />
                    <!-- <v-btn
                      small
                      color="primary"
                      @click="makeIssuer(lob.id, item.id)"
                      :disabled="!lob.traction_issue_enabled"
                    >
                      Promote To Issuer
                    </v-btn> -->
                  </p>
                </v-col>
              </v-row>
            </td>
          </template>
        </v-data-table>
        <v-btn
          :loading="loading"
          :disabled="loading"
          color="primary"
          outlined
          @click="fetchSandboxList"
        >
          Refresh
          <v-icon right dark> sync </v-icon>
        </v-btn>
      </div>
    </v-skeleton-loader>

    <h2 class="mt-12">Create a new Sandbox session</h2>
    <p>
      Create a new set of tenants, supply a "tag" label to keep track of the
      session
    </p>

    <v-skeleton-loader :loading="loading" type="article">
      <v-form ref="form" v-model="validNewSandbox" @submit.prevent="create">
        <v-row>
          <v-col>
            <v-text-field
              v-model="newTag"
              :rules="newTagRules"
              label="Tag"
              required
            ></v-text-field>
          </v-col>
          <v-col>
            <v-btn
              :disabled="!validNewSandbox"
              color="primary"
              class="mx-4"
              @click="create"
            >
              Create
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-skeleton-loader>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

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
        { text: '', value: 'data-table-expand' },
      ],
      newTag: '',
      newTagRules: [(v) => !!v || 'Tag is required'],
      loading: true,
      validNewSandbox: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes', 'currentSandbox']),
  },
  methods: {
    ...mapActions('sandbox', [
      'createSandbox',
      'getSandboxes',
      'selectSandbox',
    ]),
    async create() {
      this.loading = true;
      await this.createSandbox(this.newTag);
      await this.getSandboxes();
      this.loading = false;
    },
    async fetchSandboxList() {
      this.loading = true;
      await this.getSandboxes();
      this.loading = false;
    },
    async setTenantAsIssuer(tenantId, sandboxId) {
      this.loading = true;
      await this.makeIssuer({ tenantId: tenantId, sandboxId: sandboxId });
      await this.fetchSandboxList();
      this.loading = false;
    },
  },
  async mounted() {
    await this.fetchSandboxList();
  },
};
</script>

<style>
</style>
