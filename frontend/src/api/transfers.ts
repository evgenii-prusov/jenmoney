import { apiClient } from './client';
import type { Transfer, TransferCreate } from '../types/transfer';

const TRANSFERS_ENDPOINT = '/transfers/';

export interface TransferListResponse {
  items: Transfer[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TransferListParams {
  skip?: number;
  limit?: number;
  account_id?: number;
}

export const transfersApi = {
  createTransfer: async (transfer: TransferCreate): Promise<Transfer> => {
    const { data } = await apiClient.post<Transfer>(TRANSFERS_ENDPOINT, transfer);
    return data;
  },

  getTransfers: async (params?: TransferListParams): Promise<TransferListResponse> => {
    const { data } = await apiClient.get<TransferListResponse>(TRANSFERS_ENDPOINT, {
      params,
    });
    return data;
  },
};

export default transfersApi;