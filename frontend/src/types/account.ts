export const Currency = {
  EUR: 'EUR',
  USD: 'USD',
  RUB: 'RUB',
  JPY: 'JPY',
} as const;

export type Currency = typeof Currency[keyof typeof Currency];

export interface Account {
  id: number;
  name: string;
  currency: Currency;
  balance: number;
  balance_in_default_currency?: number | null;
  default_currency?: Currency | null;
  exchange_rate_used?: number | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  name: string;
  currency: Currency;
  balance: number;
  description?: string | null;
}

export interface AccountUpdate {
  name?: string;
  currency?: Currency;
  balance?: number;
  description?: string | null;
}

export interface AccountListResponse {
  items: Account[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

// Settings types (moved here due to Vite issue)
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