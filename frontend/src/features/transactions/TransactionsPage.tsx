import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  Button,
  Fab,
  Chip,
  TablePagination,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as IncomeIcon,
  TrendingDown as ExpenseIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  SubdirectoryArrowRight as SubdirectoryArrowRightIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { transactionsApi, type TransactionListParams } from '../../api/transactions';
import { accountsApi } from '../../api/accounts';
import { categoriesApi } from '../../api/categories';
import { TransactionForm } from '../../components/TransactionForm';
import { EditTransactionDialog } from '../../components/EditTransactionDialog';
import { DeleteTransactionDialog } from '../../components/DeleteTransactionDialog';
import type { Transaction } from '../../types/transaction';
import type { Account } from '../../types/account';
import type { Category } from '../../types/category';

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50];

export const TransactionsPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [accountFilter, setAccountFilter] = useState<number | undefined>(undefined);
  const [categoryFilter, setCategoryFilter] = useState<number | undefined>(undefined);
  const [isTransactionFormOpen, setIsTransactionFormOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);

  const queryClient = useQueryClient();

  // Transaction list query
  const transactionParams: TransactionListParams = {
    skip: page * rowsPerPage,
    limit: rowsPerPage,
    ...(accountFilter && { account_id: accountFilter }),
    ...(categoryFilter && { category_id: categoryFilter }),
  };

  const {
    data: transactionsResponse,
    isLoading: transactionsLoading,
    error: transactionsError,
  } = useQuery({
    queryKey: ['transactions', transactionParams],
    queryFn: () => transactionsApi.getTransactions(transactionParams),
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });

  // Accounts query for filter dropdown
  const { data: accountsResponse } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountsApi.getAccounts({ limit: 100 }),
  });

  // Categories query for filter dropdown (hierarchical for better UX)
  const { data: categoriesResponse } = useQuery({
    queryKey: ['categories', 'hierarchical'],
    queryFn: () => categoriesApi.getCategories(true),
  });

  const transactions = transactionsResponse?.items || [];
  const total = transactionsResponse?.total || 0;
  const accounts = accountsResponse?.items || [];
  const categories = categoriesResponse?.items || [];

  // Create account and category lookup maps
  const accountsMap = accounts.reduce((acc: Record<number, Account>, account) => {
    acc[account.id] = account;
    return acc;
  }, {});

  // Create categories map from hierarchical data (include both parent and children)
  const categoriesMap = categories.reduce((acc: Record<number, Category>, category) => {
    acc[category.id] = category;
    // Also add children to the map
    category.children?.forEach((child) => {
      acc[child.id] = child;
    });
    return acc;
  }, {});

  // Helper function to render categories with hierarchy in dropdown
  const renderCategoryMenuItems = () => {
    const items: React.ReactNode[] = [];
    
    categories.forEach((category) => {
      // Add parent category
      items.push(
        <MenuItem key={category.id} value={category.id}>
          {category.name}
        </MenuItem>
      );
      
      // Add child categories with indentation
      category.children?.forEach((child) => {
        items.push(
          <MenuItem 
            key={child.id} 
            value={child.id}
            sx={{ 
              pl: 4,
              fontSize: '0.875rem',
              color: 'text.secondary',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <SubdirectoryArrowRightIcon 
              sx={{ 
                fontSize: '1rem',
                color: 'action.active',
              }} 
            />
            {child.name}
          </MenuItem>
        );
      });
    });
    
    return items;
  };

  const handlePageChange = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleAccountFilterChange = (accountId: number | '') => {
    setAccountFilter(accountId === '' ? undefined : accountId);
    setPage(0);
  };

  const handleCategoryFilterChange = (categoryId: number | '') => {
    setCategoryFilter(categoryId === '' ? undefined : categoryId);
    setPage(0);
  };

  const handleTransactionCreate = () => {
    queryClient.invalidateQueries({ queryKey: ['transactions'] });
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
    setIsTransactionFormOpen(false);
  };

  const handleEditClick = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setIsEditDialogOpen(true);
  };

  const handleDeleteClick = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setIsDeleteDialogOpen(true);
  };

  const handleTransactionUpdate = () => {
    queryClient.invalidateQueries({ queryKey: ['transactions'] });
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
    setIsEditDialogOpen(false);
    setSelectedTransaction(null);
  };

  const handleTransactionDelete = () => {
    queryClient.invalidateQueries({ queryKey: ['transactions'] });
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
    setIsDeleteDialogOpen(false);
    setSelectedTransaction(null);
  };

  const formatAmount = (amount: number, currency: string) => {
    const formattedAmount = Math.abs(amount).toFixed(2);
    return `${formattedAmount} ${currency}`;
  };

  const getTransactionIcon = (amount: number) => {
    return amount >= 0 ? (
      <IncomeIcon color="success" fontSize="small" />
    ) : (
      <ExpenseIcon color="error" fontSize="small" />
    );
  };

  const getAmountChip = (amount: number, currency: string) => {
    return (
      <Chip
        icon={getTransactionIcon(amount)}
        label={formatAmount(amount, currency)}
        color={amount >= 0 ? 'success' : 'error'}
        variant="outlined"
        size="small"
      />
    );
  };

  if (transactionsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading transactions: {(transactionsError as Error).message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Transactions
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsTransactionFormOpen(true)}
          size="large"
        >
          Add Transaction
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Filter by Account</InputLabel>
            <Select
              value={accountFilter || ''}
              label="Filter by Account"
              onChange={(e) => handleAccountFilterChange(e.target.value as number | '')}
            >
              <MenuItem value="">All Accounts</MenuItem>
              {accounts.map((account) => (
                <MenuItem key={account.id} value={account.id}>
                  {account.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Filter by Category</InputLabel>
            <Select
              value={categoryFilter || ''}
              label="Filter by Category"
              onChange={(e) => handleCategoryFilterChange(e.target.value as number | '')}
            >
              <MenuItem value="">All Categories</MenuItem>
              {renderCategoryMenuItems()}
            </Select>
          </FormControl>

          {(accountFilter || categoryFilter) && (
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                setAccountFilter(undefined);
                setCategoryFilter(undefined);
                setPage(0);
              }}
            >
              Clear Filters
            </Button>
          )}
        </Stack>
      </Paper>

      {/* Transactions Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Account</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactionsLoading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : transactions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No transactions found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                transactions.map((transaction) => (
                  <TableRow key={transaction.id} hover>
                    <TableCell>
                      {new Date(transaction.transaction_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {accountsMap[transaction.account_id]?.name || `Account ${transaction.account_id}`}
                    </TableCell>
                    <TableCell>
                      {getAmountChip(transaction.amount, transaction.currency)}
                    </TableCell>
                    <TableCell>
                      {transaction.category_id && categoriesMap[transaction.category_id]
                        ? categoriesMap[transaction.category_id].name
                        : 'No Category'}
                    </TableCell>
                    <TableCell>
                      {transaction.description || (
                        <Typography variant="body2" color="text.secondary">
                          No description
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit transaction">
                        <IconButton
                          size="small"
                          onClick={() => handleEditClick(transaction)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete transaction">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteClick(transaction)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={handlePageChange}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleRowsPerPageChange}
          rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
        />
      </Paper>

      {/* Floating Action Button for mobile */}
      <Fab
        color="primary"
        aria-label="add transaction"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', md: 'none' },
        }}
        onClick={() => setIsTransactionFormOpen(true)}
      >
        <AddIcon />
      </Fab>

      {/* Dialogs */}
      <TransactionForm
        open={isTransactionFormOpen}
        onClose={() => setIsTransactionFormOpen(false)}
        onSuccess={handleTransactionCreate}
        accounts={accounts}
        categories={categories}
      />

      {selectedTransaction && (
        <>
          <EditTransactionDialog
            open={isEditDialogOpen}
            onClose={() => {
              setIsEditDialogOpen(false);
              setSelectedTransaction(null);
            }}
            transaction={selectedTransaction}
            onSuccess={handleTransactionUpdate}
            accounts={accounts}
            categories={categories}
          />

          <DeleteTransactionDialog
            open={isDeleteDialogOpen}
            onClose={() => {
              setIsDeleteDialogOpen(false);
              setSelectedTransaction(null);
            }}
            transaction={selectedTransaction}
            onSuccess={handleTransactionDelete}
          />
        </>
      )}
    </Box>
  );
};