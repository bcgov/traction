import { defineStore, storeToRefs } from 'pinia';
import { ref } from 'vue';
import { useConfigStore } from '../configStore';
import { UserManager } from 'oidc-client-ts';

export const useOidcStore = defineStore('oidcStore', () => {
  // Stores
  const { config } = storeToRefs(useConfigStore());

  const settings: any = {
    authority: config.value.frontend.oidc.authority,
    client_id: config.value.frontend.oidc.client,
    redirect_uri: `${window.location.origin}`,
    response_type: 'code',
    automaticSilentRenew: false,
    post_logout_redirect_uri: `${window.location.origin}`,
    loadUserInfo: true,
  };

  const userManager: UserManager = new UserManager(settings);

  userManager
    .signinRedirectCallback()
    .then(() => {
      loading.value = true;
    })
    .catch((err) => {
      console.error(err);
    });

  userManager.events.addUserLoaded(async () => {
    try {
      // Get the logged in user from the OIDC library
      const oidcUser = await userManager.getUser();
      user.value = oidcUser;

      // Strip the oidc return params
      window.history.pushState({}, document.title);
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }
  });

  // State
  const loading: any = ref(false);
  const error: any = ref(null);
  const user: any = ref(null);

  // Getters

  // Ations
  async function login() {
    loading.value = true;
    return userManager.signinRedirect();
  }

  return {
    loading,
    error,
    user,
    login,
  };
});
