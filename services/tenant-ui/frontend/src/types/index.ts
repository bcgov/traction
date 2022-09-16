interface GetItem {
  item?: {};
  loading: boolean;
  fetchItem: (id: String, params?: any) => Promise<void>;
  fetchItemWithAcapy: (id: String) => Promise<void>;
}

export type { GetItem };
