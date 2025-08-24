import React from 'react';
import { Paper, Typography, Box, Chip, CircularProgress } from '@mui/material';
import { Currency } from '../types/account';

// Define type locally to avoid Vite import issue
interface TotalBalanceType {
  total_balance: number;
  default_currency: Currency;
}

interface TotalBalanceProps {
  data: TotalBalanceType | undefined;
  loading: boolean;
}

const currencySymbols: Record<Currency, string> = {
  [Currency.EUR]: '€',
  [Currency.USD]: '$',
  [Currency.RUB]: '₽',
  [Currency.JPY]: '¥',
};

const formatBalance = (balance: number, currency: Currency): string => {
  const symbol = currencySymbols[currency];
  const formattedNumber = balance.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
  
  if (currency === Currency.EUR) {
    return `${formattedNumber} ${symbol}`;
  }
  return `${symbol}${formattedNumber}`;
};

export const TotalBalance: React.FC<TotalBalanceProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress size={24} />
      </Paper>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" color="text.secondary">
          Всего Деняк
        </Typography>
        <Chip label={data.default_currency} color="primary" size="small"/>
      </Box>
      <Typography variant="h3" color="primary" sx={{ fontWeight: 700, mb: 2 }}>
        {formatBalance(data.total_balance, data.default_currency)}
      </Typography>
    </Paper>
  );
};

export default TotalBalance;