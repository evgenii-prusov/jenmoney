import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Divider,
  Chip,
  CircularProgress,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useAccounts } from '../../../hooks/useAccounts';
import { transactionsApi } from '../../../api/transactions';
import { categoriesApi } from '../../../api/categories';
import { useBudgets } from '../../../hooks/useBudgets';
import { Currency } from '../../../types/account';

const currencySymbols: Record<Currency, string> = {
  [Currency.EUR]: '€',
  [Currency.USD]: '$',
  [Currency.RUB]: '₽',
  [Currency.JPY]: '¥',
};

export const QuickStats: React.FC = () => {
  const { data: accountsData, isLoading: accountsLoading } = useAccounts();
  
  // Fetch recent transactions for analytics
  const { data: transactionsData, isLoading: transactionsLoading } = useQuery({
    queryKey: ['transactions', { skip: 0, limit: 100 }], // Get last 100 transactions for better analytics
    queryFn: () => transactionsApi.getTransactions({ skip: 0, limit: 100 }),
    refetchInterval: 20000,
  });

  // Fetch categories for category breakdown
  const { data: categoriesData, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories', 'hierarchical'],
    queryFn: () => categoriesApi.getCategories(true),
    refetchInterval: 60000, // Refresh every minute
  });

  // Get user settings for default currency
  const { data: settingsData } = useQuery({
    queryKey: ['settings'],
    queryFn: () => import('../../../api/settings').then(m => m.settingsApi.getSettings()),
    refetchInterval: 60000,
  });

  // Get current month budgets
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;
  const { data: budgetsData } = useBudgets(currentYear, currentMonth);

  const isLoading = accountsLoading || transactionsLoading || categoriesLoading;

  if (isLoading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center', height: 'fit-content' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Quick Stats
        </Typography>
        <CircularProgress size={24} />
      </Paper>
    );
  }

  if (!accountsData || accountsData.items.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center', height: 'fit-content' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Quick Stats
        </Typography>
        <Typography variant="body2" color="text.secondary">
          No accounts yet. Start by creating your first account!
        </Typography>
      </Paper>
    );
  }

  const accounts = accountsData.items;
  const transactions = transactionsData?.items || [];
  const categories = categoriesData?.items || [];
  const budgets = budgetsData?.items || [];
  const defaultCurrency = settingsData?.default_currency || Currency.USD;
  
  // Group accounts by currency
  const accountsByCurrency = accounts.reduce((acc, account) => {
    const currency = account.currency;
    if (!acc[currency]) {
      acc[currency] = { count: 0, balance: 0 };
    }
    acc[currency].count += 1;
    acc[currency].balance += account.balance;
    return acc;
  }, {} as Record<string, { count: number; balance: number }>);

  // Find highest balance account
  const highestBalanceAccount = accounts.reduce((max, account) => 
    account.balance > max.balance ? account : max
  );

  // Calculate transaction analytics - simplified without currency conversion for now
  // Note: In a real implementation, we'd need proper currency conversion rates
  const totalTransactions = transactions.length;
  
  // Get the most recent 30 days for trend analysis
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  
  const recentTransactions = transactions.filter(t => 
    new Date(t.transaction_date) >= thirtyDaysAgo
  );
  
  // For simplicity, we'll calculate totals without currency conversion
  // This is a limitation that should be addressed with proper currency conversion API
  const recentIncome = recentTransactions.filter(t => t.amount > 0).reduce((sum, t) => sum + t.amount, 0);
  const recentExpenses = Math.abs(recentTransactions.filter(t => t.amount < 0).reduce((sum, t) => sum + t.amount, 0));

  // Use default currency symbol for display
  const defaultCurrencySymbol = currencySymbols[defaultCurrency];

  // Category breakdown for recent expenses
  const categoryMap = categories.reduce((acc, cat) => {
    acc[cat.id] = cat;
    return acc;
  }, {} as Record<number, any>);

  const expensesByCategory = recentTransactions
    .filter(t => t.amount < 0 && t.category_id)
    .reduce((acc, t) => {
      const categoryId = t.category_id!;
      const category = categoryMap[categoryId];
      if (category) {
        const categoryName = category.name;
        if (!acc[categoryName]) {
          acc[categoryName] = 0;
        }
        acc[categoryName] += Math.abs(t.amount);
      }
      return acc;
    }, {} as Record<string, number>);

  const topCategories = Object.entries(expensesByCategory)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  // Monthly comparison (current vs previous month)
  const currentMonthStart = new Date(currentYear, currentMonth - 1, 1);
  const currentMonthTransactions = transactions.filter(t => 
    new Date(t.transaction_date) >= currentMonthStart
  );
  
  const prevMonthStart = new Date(currentYear, currentMonth - 2, 1);
  const prevMonthEnd = new Date(currentYear, currentMonth - 1, 0);
  const prevMonthTransactions = transactions.filter(t => {
    const date = new Date(t.transaction_date);
    return date >= prevMonthStart && date <= prevMonthEnd;
  });

  const currentMonthExpenses = Math.abs(currentMonthTransactions.filter(t => t.amount < 0).reduce((sum, t) => sum + t.amount, 0));
  const prevMonthExpenses = Math.abs(prevMonthTransactions.filter(t => t.amount < 0).reduce((sum, t) => sum + t.amount, 0));
  
  const expensesTrend = prevMonthExpenses > 0 ? 
    ((currentMonthExpenses - prevMonthExpenses) / prevMonthExpenses) * 100 : 0;

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Quick Stats
      </Typography>
      {/* Transaction Stats */}
      {totalTransactions > 0 ? (
        <>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Activity (Last 30 days)
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              {recentTransactions.length} transactions
            </Typography>

            {/* Monthly trend */}
            {prevMonthExpenses > 0 && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {expensesTrend > 0 ? (
                  <TrendingUpIcon sx={{ fontSize: 16, color: 'error.main' }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 16, color: 'success.main' }} />
                )}
                <Typography variant="body2" color={expensesTrend > 0 ? 'error.main' : 'success.main'}>
                  {Math.abs(expensesTrend).toFixed(1)}% vs last month
                </Typography>
              </Box>
            )}
          </Box>

          {/* Income vs Expenses */}
          {(recentIncome > 0 || recentExpenses > 0) && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Income vs Expenses (Mixed Currencies)
              </Typography>
              <Box sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2" color="success.main">
                    Income
                  </Typography>
                  <Typography variant="body2" color="success.main" sx={{ fontWeight: 500 }}>
                    {defaultCurrencySymbol}{recentIncome.toLocaleString()}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={recentIncome > 0 ? Math.min((recentIncome / (recentIncome + recentExpenses)) * 100, 100) : 0}
                  sx={{ 
                    height: 6, 
                    borderRadius: 3,
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: 'success.main',
                    }
                  }} 
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2" color="error.main">
                    Expenses
                  </Typography>
                  <Typography variant="body2" color="error.main" sx={{ fontWeight: 500 }}>
                    {defaultCurrencySymbol}{recentExpenses.toLocaleString()}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={recentExpenses > 0 ? Math.min((recentExpenses / (recentIncome + recentExpenses)) * 100, 100) : 0}
                  sx={{ 
                    height: 6, 
                    borderRadius: 3,
                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: 'error.main',
                    }
                  }} 
                />
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                * Amounts shown without currency conversion
              </Typography>
            </Box>
          )}

          {/* Top expense categories - Enhanced visibility */}
          {topCategories.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                🏷️ Top 3 Expense Categories
              </Typography>
              <Box sx={{ 
                backgroundColor: 'background.default', 
                borderRadius: 1, 
                p: 1.5,
                border: '1px solid',
                borderColor: 'divider'
              }}>
                {topCategories.map(([category, amount], index) => (
                  <Box key={category} sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    mb: index < topCategories.length - 1 ? 1 : 0,
                    p: 0.5,
                    borderRadius: 0.5,
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" color="primary" sx={{ fontWeight: 500, minWidth: '20px' }}>
                        #{index + 1}
                      </Typography>
                      <Typography variant="body2" noWrap sx={{ maxWidth: '120px' }}>
                        {category}
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'error.main' }}>
                      {defaultCurrencySymbol}{amount.toLocaleString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          {/* Budget status */}
          {budgets.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Budget Status
              </Typography>
              <Tooltip title={`${budgets.length} active budgets this month`}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {budgets.length} budget{budgets.length > 1 ? 's' : ''} active
                </Typography>
              </Tooltip>
            </Box>
          )}

          <Divider sx={{ my: 2 }} />
        </>
      ) : null}

      {/* Currency breakdown */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          By Currency
        </Typography>
        {Object.entries(accountsByCurrency).map(([currency, data]) => (
          <Box key={currency} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label={currency} size="small" variant="outlined" />
              <Typography variant="body2">
                {data.count} account{data.count > 1 ? 's' : ''}
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              {currencySymbols[currency as Currency]}{data.balance.toLocaleString()}
            </Typography>
          </Box>
        ))}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Top account */}
      <Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Top Account
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {highestBalanceAccount.name}
        </Typography>
        <Typography variant="body1" color="primary" sx={{ fontWeight: 600 }}>
          {currencySymbols[highestBalanceAccount.currency]}{highestBalanceAccount.balance.toLocaleString()}
        </Typography>
      </Box>
    </Paper>
  );
};

export default QuickStats;