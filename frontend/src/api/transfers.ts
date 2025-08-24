import { apiClient } from './client';
import type { Transfer, TransferCreate } from '../types/transfer';

const TRANSFERS_ENDPOINT = '/transfers/';

interface TransferListResponse {
  items: Transfer[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const transfersApi = {
  createTransfer: async (transfer: TransferCreate): Promise<Transfer> => {
    const { data } = await apiClient.post<Transfer>(TRANSFERS_ENDPOINT, transfer);
    return data;
  },

  getTransfers: async (): Promise<Transfer[]> => {
    const { data } = await apiClient.get<TransferListResponse>(TRANSFERS_ENDPOINT);
    return data.items;
  },
};

export default transfersApi;