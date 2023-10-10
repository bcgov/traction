import { Ref } from 'vue';
import { useToast } from 'vue-toastification';

import {
  CredDefStorageRecord,
  CredentialDefinitionSendRequest,
} from '@/types/acapyApi/acapyInterface';

const toast = useToast();

const loadedInterval = (
  credDef: CredentialDefinitionSendRequest,
  getStoredCredDefs: () => Promise<CredDefStorageRecord[] | undefined>,
  loadTable: Function,
  message: string,
  setSelected: Ref<CredDefStorageRecord | undefined> | undefined = undefined,
  attempts: number = 10,
  intervalMilliseconds: number = 500
) => {
  const interval = setInterval(async () => {
    if (attempts < 1) {
      clearInterval(interval);
    }
    try {
      const storedCredDefs = await getStoredCredDefs();
      const newCredDef = storedCredDefs?.find(
        (c: CredDefStorageRecord) =>
          c.schema_id === credDef.schema_id && c.tag === credDef.tag
      );
      if (newCredDef) {
        clearInterval(interval);
        loadTable();
        toast.success(message);
        if (setSelected) setSelected.value = newCredDef;
      }
    } catch (err) {
      console.error(err);
      clearInterval(interval);
    }
    attempts -= 1;
  }, intervalMilliseconds);
};

export default loadedInterval;
