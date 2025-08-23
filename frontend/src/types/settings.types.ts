import { Currency } from './account';

export interface UserSettings {
  id: number;
  default_currency: Currency;
  created_at: string;
  updated_at: string;
}

export interface UserSettingsUpdate {
  default_currency?: Currency;
}

export interface TotalBalance {
  total_balance: number;
  default_currency: Currency;
  currency_breakdown: Record<string, number>;
}