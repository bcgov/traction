import { useToast } from 'vue-toastification';
import { Ref } from 'vue';

import { SchemaSendRequest } from '@/types/acapyApi/acapyInterface';
import { SchemaStorageRecord } from '@/types';

const toast = useToast();

const loadedInterval = (
  schema: SchemaSendRequest,
  getStoredSchemas: () => Promise<SchemaStorageRecord[] | undefined>,
  loadTable: Function,
  message: string,
  setSelected: Ref<SchemaStorageRecord | undefined> | undefined = undefined,
  attempts: number = 10,
  intervalMilliseconds: number = 500
) => {
  const interval = setInterval(async () => {
    if (attempts < 1) {
      clearInterval(interval);
    }
    try {
      const storedSchemas = await getStoredSchemas();
      const newSchema = storedSchemas?.find(
        (s: SchemaStorageRecord) =>
          s.schema.name === schema.schema_name &&
          s.schema.version === schema.schema_version
      );
      if (newSchema) {
        clearInterval(interval);
        loadTable();
        toast.success(message);
        if (setSelected) setSelected.value = newSchema;
      }
    } catch (err) {
      console.error(err);
      clearInterval(interval);
    }
    attempts -= 1;
  }, intervalMilliseconds);
};

export default loadedInterval;
