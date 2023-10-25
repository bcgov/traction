import { EndorserInfo, TAAInfo } from '@/types/acapyApi/acapyInterface';

import { API_PATH } from '@/helpers/constants';
import { defineStore, storeToRefs } from 'pinia';
import { computed, ref, Ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import { useTokenStore } from './tokenStore';
import { fetchItem } from './utils/fetchItem';

export const useTenantStore = defineStore('tenant', () => {
  // state
  const tenant: any = ref(null);
  const loading: Ref<boolean> = ref(false);
  const loadingIssuance: Ref<boolean> = ref(false);
  const error: any = ref(null);
  const endorserConnection: any = ref(null);
  const endorserInfo: Ref<EndorserInfo | null> = ref(null);
  const publicDid: any = ref(null);
  const writeLedger: any = ref(null);
  const publicDidRegistrationProgress: Ref<string> = ref('');
  const taa: Ref<any> = ref(null);
  const tenantConfig: any = ref(null);
  const tenantWallet: any = ref(null);
  const tenantDefaultSettings: any = ref(null);

  const { token } = storeToRefs(useTokenStore());
  const acapyApi = useAcapyApi();

  // getters
  const tenantReady = computed(() => {
    return token.value != null;
  });
  const isIssuer = computed(() => {
    return (
      endorserConnection.value &&
      endorserConnection.value.state === 'active' &&
      publicDid.value &&
      publicDid.value.did
    );
  });

  // actions
  function clearTenant() {
    console.log('> clearTenant');
    tenant.value = null;
    localStorage.removeItem('tenant');
    localStorage.removeItem('tenantConfig');
    localStorage.removeItem('tenantTaa');
    localStorage.removeItem('tenantEndorserInfo');
    localStorage.removeItem('tenantEndorserConnection');
    console.log('< clearTenant');
  }

  async function getSelf() {
    tenant.value = await fetchItem(API_PATH.TENANT_SELF, '', error, loading);
    localStorage.setItem('tenant', JSON.stringify(tenant.value));
  }

  async function getTenantConfig() {
    tenantConfig.value = await fetchItem(
      API_PATH.TENANT_CONFIG,
      '',
      error,
      loading
    );
    localStorage.setItem('tenantConfig', JSON.stringify(tenantConfig.value));
    if (tenantConfig.value.curr_ledger_id) {
      writeLedger.value = {
        ledger_id: tenantConfig.value.curr_ledger_id,
      };
    }
  }

  async function getIssuanceStatus() {
    console.log('> tenantStore.getIssuanceStatus');
    loadingIssuance.value = true;
    // Find out issuer status when logging in
    const result = await Promise.allSettled([
      getWriteLedger(),
      getTaa(),
      getEndorserInfo(),
      getEndorserConnection(),
      getPublicDid(),
    ]);
    loadingIssuance.value = false;
    if (result) {
      const errors = result.filter(
        (res): res is PromiseRejectedResult => res.status === 'rejected'
      );
      if (errors?.length) {
        console.log(errors);
        throw Error(errors[0]?.reason);
      }
    }
    console.log('< tenantStore.getIssuanceStatus');
  }

  async function getEndorserConnection() {
    console.log('> tenantStore.getEndorserConnection');
    // Don't override the loader if it's already going from something else
    const loadingTrack = !loadingIssuance.value ? loadingIssuance : ref(false);
    error.value = null;
    loadingTrack.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_ENDORSER_CONNECTION)
      .then((res: any) => {
        endorserConnection.value = res.data;
        localStorage.setItem(
          'tenantEndorserConnection',
          JSON.stringify(endorserConnection.value)
        );
      })
      .catch((err) => {
        endorserConnection.value = null;
        if (err.response && err.response.status === 404) {
          // 404s are not errors here
        } else {
          error.value = err;
        }
      })
      .finally(() => {
        loadingTrack.value = false;
      });
    console.log('< tenantStore.getEndorserConnection');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return endorserConnection.value;
  }

  async function getEndorserInfo() {
    console.log('> tenantStore.getEndorserInfo');
    // Don't override the loader if it's already going from something else
    const loadingTrack = !loadingIssuance.value ? loadingIssuance : ref(false);
    error.value = null;
    loadingTrack.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_ENDORSER_INFO)
      .then((res: any) => {
        endorserInfo.value = res.data;
        localStorage.setItem(
          'tenantEndorderInfo',
          JSON.stringify(endorserInfo.value)
        );
      })
      .catch((err) => {
        error.value = err;
        endorserInfo.value = null;
      })
      .finally(() => {
        loadingTrack.value = false;
      });
    console.log('< tenantStore.getEndorserInfo');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return endorserInfo.value;
  }

  async function connectToEndorser(quickConnect = false) {
    console.log('> tenantStore.connectToEndorser');
    error.value = null;
    loadingIssuance.value = true;

    try {
      publicDidRegistrationProgress.value = 'Connecting to Endorser';
      const res = await acapyApi.postHttp(
        API_PATH.TENANT_ENDORSER_CONNECTION,
        {}
      );
      endorserConnection.value = res.data;
      if (quickConnect) {
        // If you've marked this endorser as 'quick connect' (no intervention)
        // then wait for it to automatically become active
        await waitForActiveEndorserConnection();
      }
    } catch (err) {
      error.value = err;
    } finally {
      loadingIssuance.value = false;
    }

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  async function getPublicDid() {
    console.log('> tenantStore.getPublicDid');
    publicDid.value = await fetchItem(
      API_PATH.WALLET_DID_PUBLIC,
      '',
      error,
      !loadingIssuance.value ? loadingIssuance : ref(false)
    );
    localStorage.setItem('tenantPublicDid', JSON.stringify(publicDid.value));
    console.log('< tenantStore.getPublicDid');
  }

  async function getWriteLedger() {
    console.log('> tenantStore.getWriteLedger');
    writeLedger.value = await fetchItem(
      API_PATH.TENANT_GET_WRITE_LEDGER,
      '',
      error,
      !loadingIssuance.value ? loadingIssuance : ref(false)
    );
  }

  async function setWriteLedger(ledger_id: string) {
    console.log('> tenantStore.setWriteLedger');
    const res = await acapyApi.putHttp(
      API_PATH.TENANT_SWITCH_WRITE_LEDGER(ledger_id)
    );
    if (!res.data.write_ledger) {
      throw Error('No write_ledger in set write ledger response');
    }
    const curr_ledger_id = res.data.write_ledger;
    writeLedger.value = {
      ledger_id: curr_ledger_id,
    };
    console.log('< tenantStore.setWriteLedger');
  }

  async function waitForTxnCompletion(txnId: string) {
    let retries = 0;
    publicDidRegistrationProgress.value = 'Waiting for transaction to complete';
    for (;;) {
      const pRes = await acapyApi.getHttp(API_PATH.TRANSACTION_GET(txnId));
      if (pRes.data.state === 'transaction_acked') {
        publicDidRegistrationProgress.value = '';
        return;
      }
      if (retries > 10) {
        break;
      }
      retries = retries + 1;
      await new Promise((r) => setTimeout(r, retries * 1000));
    }
    throw Error(`Transaction ${txnId} has not been completed`);
  }

  async function waitForActiveEndorserConnection(maxRetries = 10) {
    const connId = endorserConnection.value.connection_id;
    let retries = 0;
    publicDidRegistrationProgress.value =
      'Waiting for Endorser connection to become active';
    loadingIssuance.value = true;
    for (;;) {
      const res = await acapyApi.getHttp(API_PATH.CONNECTION(connId), {});
      endorserConnection.value = res.data;
      if (endorserConnection.value.state === 'active') {
        console.log(`Endorser connection ${connId} state is active`);
        publicDidRegistrationProgress.value = '';
        loadingIssuance.value = false;
        return;
      }
      if (retries > maxRetries) {
        break;
      }
      retries = retries + 1;
      await new Promise((r) => setTimeout(r, 1000));
    }
  }

  async function registerPublicDid() {
    console.log('> connectionStore.registerPublicDid');
    error.value = null;
    loadingIssuance.value = true;
    publicDidRegistrationProgress.value = '';
    let postedDID: any = null;
    try {
      // Create a DID
      publicDidRegistrationProgress.value = 'Creating DID';
      const aRes = await acapyApi.postHttp(API_PATH.WALLET_DID_CREATE, {
        method: 'sov',
        options: { key_type: 'ed25519' },
      });
      if (!aRes.data.result) {
        throw Error('No result in create DID response');
      }

      // Use the did and verkey
      const did = aRes.data.result.did;
      const verkey = aRes.data.result.verkey;
      const alias = tenant.value.tenant_name || tenant.value.wallet_id;
      // Register the DID
      publicDidRegistrationProgress.value = 'Registering the DID';
      const bRes = await acapyApi.postHttp(
        `${API_PATH.TENANT_REGISTER_PUBLIC_DID}?did=${did}&verkey=${verkey}&alias=${alias}`,
        {}
      );
      console.log(bRes);
      console.log(`posted ${did} on ledger ${writeLedger.value.ledger_id}`);

      // TODO: should this be here? Or register and assign as 2 different buttons...?
      // Wait for endorse transaction completion
      const txnId = bRes.data.txn.transaction_id;
      waitForTxnCompletion(txnId);
      // Verify DID is posted on correct ledger
      const cRes = await acapyApi.getHttp(
        `${API_PATH.TENANT_GET_VERKEY_POSTED_DID}?did=${did}`,
        {}
      );
      publicDidRegistrationProgress.value = 'Verifying DID posted on ledger';
      if (!cRes.data.verkey) {
        console.log(`DID ${did} is not posted on ledger`);
        postedDID = null;
      } else if (cRes.data && cRes.data.ledger_id) {
        const posted_did_ledger_id = cRes.data.ledger_id;
        console.log(
          `Verified DID ${did} is posted on ledger ${posted_did_ledger_id}`
        );
        if (posted_did_ledger_id === writeLedger.value.ledger_id) {
          postedDID = did;
        } else {
          postedDID = null;
        }
      } else {
        postedDID = did;
      }
      // Assign the public DID
      console.log(`calling /wallet/did/public with ${postedDID}`);
      publicDidRegistrationProgress.value = 'Assigning the public DID';
      const dRes = await acapyApi.postHttp(
        `${API_PATH.WALLET_DID_PUBLIC}?did=${postedDID}`,
        {}
      );
      publicDidRegistrationProgress.value = 'Fetching created public DID';
      // set curr_ledger_id in TenantRecord
      const payload = {
        ledger_id: writeLedger.value.ledger_id,
      };
      const eRes = await acapyApi.putHttp(
        API_PATH.TENANT_CONFIG_SET_LEDGER_ID,
        payload
      );
      getWriteLedger();
      getPublicDid();
    } catch (err) {
      error.value = err;
    } finally {
      publicDidRegistrationProgress.value = '';
      loadingIssuance.value = false;
    }
    console.log('< connectionStore.registerPublicDid');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  async function getTenantSubWallet() {
    console.log('> tenantStore.getSubWallet');
    error.value = null;
    loading.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_WALLET)
      .then((res: any) => {
        tenantWallet.value = res.data;
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.getSubWallet');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantWallet.value;
  }

  async function getTenantDefaultSettings() {
    console.log('> tenantStore.getTenantDefaultSettings');
    error.value = null;
    loading.value = true;
    tenantDefaultSettings.value = await fetchItem(
      API_PATH.TENANT_SETTINGS,
      '',
      error,
      loading
    );
    console.log('< tenantStore.getTenantDefaultSettings');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantDefaultSettings.value;
  }

  async function updateTenantSubWallet(payload: object) {
    console.log('> tenantStore.updateTenantSubWallet');
    error.value = null;
    loading.value = true;

    await acapyApi
      .putHttp(API_PATH.TENANT_WALLET, payload)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.updateTenantSubWallet');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  async function getTaa() {
    taa.value = await fetchItem(
      API_PATH.LEDGER_TAA,
      '',
      error,
      !loadingIssuance.value ? loadingIssuance : ref(false)
    );
    localStorage.setItem('tenantTaa', JSON.stringify(taa.value));
  }

  async function acceptTaa(payload: object) {
    console.log('> tenantStore.acceptTaa');
    error.value = null;
    loadingIssuance.value = true;

    try {
      await acapyApi.postHttp(API_PATH.LEDGER_TAA_ACCEPT, payload);
      await getTaa();
    } catch (err) {
      error.value = err;
    } finally {
      loadingIssuance.value = false;
    }
    console.log('< tenantStore.acceptTaa');
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  function setTenantLoginDataFromLocalStorage() {
    console.log('> setTenantFromLocalStorage');
    try {
      const savedTenant = localStorage.getItem('tenant');
      tenant.value = savedTenant ? JSON.parse(savedTenant) : null;

      const savedTenantConfig = localStorage.getItem('tenantConfig');
      tenantConfig.value = savedTenantConfig
        ? JSON.parse(savedTenantConfig)
        : null;

      const savedTaa = localStorage.getItem('tenantTaa');
      taa.value = savedTaa ? JSON.parse(savedTaa) : null;

      const savedEndorserInfo = localStorage.getItem('tenantEndorserInfo');
      endorserInfo.value = savedEndorserInfo
        ? JSON.parse(savedEndorserInfo)
        : null;

      const savedEndorserConnection = localStorage.getItem(
        'tenantEndorserConnection'
      );
      endorserConnection.value = savedEndorserConnection
        ? JSON.parse(savedEndorserConnection)
        : null;

      const savedPublicDid = localStorage.getItem('tenantPublicDid');
      publicDid.value = savedPublicDid ? JSON.parse(savedPublicDid) : null;
    } catch (err) {
      console.info('Error processing tenant info from local storage');
      console.error(err);
    }

    console.log('< setTenantFromLocalStorage');
  }

  return {
    loading,
    loadingIssuance,
    error,
    tenant,
    endorserConnection,
    endorserInfo,
    publicDid,
    writeLedger,
    taa,
    tenantReady,
    isIssuer,
    publicDidRegistrationProgress,
    tenantConfig,
    tenantWallet,
    tenantDefaultSettings,
    getSelf,
    getTenantConfig,
    getIssuanceStatus,
    clearTenant,
    setTenantLoginDataFromLocalStorage,
    getEndorserConnection,
    getEndorserInfo,
    getTenantDefaultSettings,
    connectToEndorser,
    getPublicDid,
    getWriteLedger,
    setWriteLedger,
    registerPublicDid,
    waitForActiveEndorserConnection,
    getTenantSubWallet,
    updateTenantSubWallet,
    getTaa,
    acceptTaa,
  };
});

export default {
  useTenantStore,
};
