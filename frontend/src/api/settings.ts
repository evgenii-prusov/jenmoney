import { apiClient } from './client';
import { Currency } from '../types/account';

// Define types locally to avoid Vite import issue
interface UserSettings {
  id: number;
  default_currency: Currency;
  created_at: string;
  updated_at: string;
}

interface UserSettingsUpdate {
  default_currency?: Currency;
}

interface TotalBalance {
  total_balance: number;
  default_currency: Currency;
  currency_breakdown: Record<string, number>;
}

export const settingsApi = {
  getSettings: async (): Promise<UserSettings> => {
    const response = await apiClient.get<UserSettings>('/settings/');
    return response.data;
  },

  updateSettings: async (settings: UserSettingsUpdate): Promise<UserSettings> => {
    const response = await apiClient.patch<UserSettings>('/settings/', settings);
    return response.data;
  },

  getTotalBalance: async (): Promise<TotalBalance> => {
    const response = await apiClient.get<TotalBalance>('/accounts/total-balance/');
    return response.data;
  },
};