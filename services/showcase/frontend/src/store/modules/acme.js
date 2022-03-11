// The store module to hold the "Acme" tenant components
export default {
  namespaced: true,
  state: {
    selectedApplicant: null,
    tenant: {}
  },
  getters: {
    selectedApplicant: state => state.selectedApplicant,
    tenant: state => state.tenant
  },
  mutations: {
    SET_SELECTED_APPLICANT(state, applicant) {
      state.selectedApplicant = applicant;
    },
    SET_TENANT(state, tenant) {
      state.tenant = tenant;
    }
  },
  actions: {}
};
