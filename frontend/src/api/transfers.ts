import { apiClient } from './client';
import type { Transfer, TransferCreate, TransferUpdate } from '../types/transfer';

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

  getTransfer: async (id: number): Promise<Transfer> => {
    const { data } = await apiClient.get<Transfer>(`${TRANSFERS_ENDPOINT}${id}`);
    return data;
  },

  updateTransfer: async (id: number, transfer: TransferUpdate): Promise<Transfer> => {
    const { data } = await apiClient.patch<Transfer>(`${TRANSFERS_ENDPOINT}${id}`, transfer);
    return data;
  },

  deleteTransfer: async (id: number): Promise<Transfer> => {
    const { data } = await apiClient.delete<Transfer>(`${TRANSFERS_ENDPOINT}${id}`);
    return data;
  },
};

export default transfersApi;