// import { apiClient } from './client';
import type { Transfer, TransferCreate } from '../types/transfer';

// const TRANSFERS_ENDPOINT = '/transfers/';

export const transfersApi = {
  createTransfer: async (transfer: TransferCreate): Promise<Transfer> => {
    // Placeholder for future backend implementation
    // For now, return a mock response to test the UI
    console.log('Transfer API call (placeholder):', transfer);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock response for UI testing
    const mockTransfer: Transfer = {
      id: Date.now(),
      from_account_id: transfer.from_account_id,
      to_account_id: transfer.to_account_id,
      from_amount: transfer.from_amount,
      to_amount: transfer.to_amount,
      from_currency: 'EUR', // This would come from actual account data
      to_currency: 'USD', // This would come from actual account data
      description: transfer.description,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    return mockTransfer;
    
    // Future implementation:
    // const { data } = await apiClient.post<Transfer>(TRANSFERS_ENDPOINT, transfer);
    // return data;
  },

  getTransfers: async (): Promise<Transfer[]> => {
    // Placeholder for future backend implementation
    console.log('Get transfers API call (placeholder)');
    
    // For now, return empty array
    return [];
    
    // Future implementation:
    // const { data } = await apiClient.get<Transfer[]>(TRANSFERS_ENDPOINT);
    // return data;
  },
};

export default transfersApi;