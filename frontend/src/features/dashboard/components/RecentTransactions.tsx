import React from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  TrendingUp as IncomeIcon,
  TrendingDown as ExpenseIcon,
  Receipt as TransactionIcon,
} from '@mui/icons-material';
import { Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { transactionsApi } from '../../../api/transactions';
import { accountsApi } from '../../../api/accounts';
import { categoriesApi } from '../../../api/categories';
import { CategoryDisplay, createCategoryMap } from '../../../components/CategoryDisplay';
import { Currency } from '../../../types/account';
import type { Account } from '../../../types/account';

const currencySymbols: Record<Currency, string> = {
  [Currency.EUR]: '€',
  [Currency.USD]: '$',
  [Currency.RUB]: '₽',
  [Currency.JPY]: '¥',
};

const formatAmount = (amount: number, currency: Currency): string => {
  const symbol = currencySymbols[currency];
  const formattedNumber = Math.abs(amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  if (currency === Currency.EUR) {
    return `${formattedNumber} ${symbol}`;
  }
  return `${symbol}${formattedNumber}`;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) {
    return 'Today';
  } else if (diffDays === 2) {
    return 'Yesterday';
  } else if (diffDays <= 7) {
    return `${diffDays - 1} days ago`;
  } else {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  }
};

export const RecentTransactions: React.FC = () => {
  // Fetch recent transactions (last 3)
  const {
    data: transactionsResponse,
    isLoading: transactionsLoading,
    error: transactionsError,
  } = useQuery({
    queryKey: ['transactions', { skip: 0, limit: 3 }],
    queryFn: () => transactionsApi.getTransactions({ skip: 0, limit: 3 }),
    refetchInterval: 5000,
  });

  // Fetch accounts for lookup
  const { data: accountsResponse } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountsApi.getAccounts({ limit: 100 }),
  });

  // Fetch categories for lookup
  const { data: categoriesResponse } = useQuery({
    queryKey: ['categories', 'hierarchical'],
    queryFn: () => categoriesApi.getCategories(true),
  });

  const transactions = transactionsResponse?.items || [];
  const accounts = accountsResponse?.items || [];
  const categories = categoriesResponse?.items || [];

  // Create lookup maps
  const accountsMap = accounts.reduce((acc: Record<number, Account>, account) => {
    acc[account.id] = account;
    return acc;
  }, {});

  const categoryMap = createCategoryMap(categories);

  if (transactionsError) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Transactions
        </Typography>
        <Alert severity="error">
          Failed to load recent transactions. Please try again later.
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Recent Transactions
        </Typography>
        <Button
          component={Link}
          to="/transactions"
          size="small"
          sx={{ textTransform: 'none' }}
        >
          View All
        </Button>
      </Box>

      {transactionsLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={24} />
        </Box>
      ) : transactions.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <TransactionIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            No transactions yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Start by creating an account and adding transactions
          </Typography>
        </Box>
      ) : (
        <List sx={{ p: 0 }}>
          {transactions.map((transaction, index) => {
            const account = accountsMap[transaction.account_id];
            const isIncome = transaction.amount > 0;
            
            return (
              <React.Fragment key={transaction.id}>
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon>
                    {isIncome ? (
                      <IncomeIcon sx={{ color: 'success.main' }} />
                    ) : (
                      <ExpenseIcon sx={{ color: 'error.main' }} />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">
                          {transaction.description || 'Untitled Transaction'}
                        </Typography>
                        <Typography 
                          variant="body1" 
                          sx={{ 
                            fontWeight: 600,
                            color: isIncome ? 'success.main' : 'error.main'
                          }}
                        >
                          {isIncome ? '+' : ''}{formatAmount(transaction.amount, transaction.currency)}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          <Typography variant="body2" color="text.secondary">
                            {account?.name || 'Unknown Account'}
                          </Typography>
                          {transaction.category_id && categoryMap[transaction.category_id] && (
                            <>
                              <Typography variant="body2" color="text.secondary">
                                •
                              </Typography>
                              <CategoryDisplay 
                                category={categoryMap[transaction.category_id]} 
                                variant="inline"
                              />
                            </>
                          )}
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(transaction.transaction_date)}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < transactions.length - 1 && <Divider />}
              </React.Fragment>
            );
          })}
        </List>
      )}
    </Paper>
  );
};

export default RecentTransactions;