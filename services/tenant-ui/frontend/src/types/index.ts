export interface GetItem {
  item?: any;
  loading: boolean;
  fetchItem: (id: string, params?: any) => Promise<void>;
}
