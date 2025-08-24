import { apiClient } from './client';
import type { Transfer, TransferCreate } from '../types/transfer';

const TRANSFERS_ENDPOINT = '/transfers/';

export const transfersApi = {
  createTransfer: async (transfer: TransferCreate): Promise<Transfer> => {
    // Future implementation when backend is ready:
    const { data } = await apiClient.post<Transfer>(TRANSFERS_ENDPOINT, transfer);
    return data;
    
    // Placeholder implementation for testing:
    // console.log('Transfer API call (placeholder):', transfer);
    // await new Promise(resolve => setTimeout(resolve, 1000));
    // const mockTransfer: Transfer = {
    //   id: Date.now(),
    //   from_account_id: transfer.from_account_id,
    //   to_account_id: transfer.to_account_id,
    //   from_amount: transfer.from_amount,
    //   to_amount: transfer.to_amount,
    //   from_currency: 'EUR',
    //   to_currency: 'USD',
    //   description: transfer.description,
    //   created_at: new Date().toISOString(),
    //   updated_at: new Date().toISOString(),
    // };
    // return mockTransfer;
  },

  getTransfers: async (): Promise<Transfer[]> => {
    // Future implementation when backend is ready:
    const { data } = await apiClient.get<Transfer[]>(TRANSFERS_ENDPOINT);
    return data;
  },
};

export default transfersApi;