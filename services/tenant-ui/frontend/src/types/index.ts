interface GetItem {
  item?: {};
  loading: boolean;
  fetchItem: (id: string, params?: any) => Promise<void>;
  fetchItemWithAcapy: (id: string) => Promise<void>;
}

export type { GetItem };
