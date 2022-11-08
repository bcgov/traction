import axios from 'axios';
import { defineStore, storeToRefs } from 'pinia';
import { computed, ref } from 'vue';
import { useConfigStore } from '../configStore';
import { useInnkeeperTokenStore } from './innkeeperTokenStore';
import { UserManager } from 'oidc-client-ts';

export const useInnkeeperOidcStore = defineStore('innkeeperOidcStore', () => {
  // other stores
  const { config } = storeToRefs(useConfigStore());
  const { token } = storeToRefs(useInnkeeperTokenStore());

  // private (move to other file maybe?)
  let _userManager: UserManager;
  const _settings: any = {
    authority: config.value.frontend.oidc.authority,
    client_id: config.value.frontend.oidc.client,
    redirect_uri: `${window.location.origin}/innkeeper`,
    response_type: 'code',
    automaticSilentRenew: false, // don't need to renew for our needs at this point
    post_logout_redirect_uri: `${window.location.origin}/innkeeper`,
    loadUserInfo: true,
  };
  _userManager = new UserManager(_settings);

  _userManager
    .signinRedirectCallback()
    .then(function (user) {
      console.log('signed in', user);
    })
    .catch(function (err) {
      console.error(err);
    });

  _userManager.events.addUserLoaded(async () => {
    await _userManager
      .getUser()
      .then((usr) => {
        user.value = usr;
        const config = {
          headers: { Authorization: `Bearer ${usr?.access_token}` },
        };
        axios
          .get('/api/innkeeperLogin', config)
          .then((res) => {
            token.value = res.data.access_token;
          })
          .catch((err) => {
            error.value = err;
            console.error(error.value);
          });
      })
      .catch((err) => {
        error.value = err;
        console.error(error.value);
      });

    if (error.value != null) {
      // throw error so callers can handle appropriately
      throw error.value;
    }
  });

  // state
  const loading: any = ref(false);
  const error: any = ref(null);
  const user: any = ref(null);

  // getters

  // actions
  async function login() {
    return _userManager.signinRedirect();
  }

  return {
    loading,
    error,
    login,
    user,
  };
});

export default {
  useInnkeeperOidcStore,
};
