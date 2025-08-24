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
  SwapHoriz as SwapHorizIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { transfersApi, type TransferListParams } from '../../api/transfers';
import { accountsApi } from '../../api/accounts';
import { TransferForm } from '../../components/TransferForm';
import { EditTransferDialog } from '../../components/EditTransferDialog';
import { DeleteTransferDialog } from '../../components/DeleteTransferDialog';
import type { Transfer, TransferUpdate, TransferCreate } from '../../types/transfer';

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50];

export const TransfersPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [accountFilter, setAccountFilter] = useState<number | undefined>(undefined);
  const [isTransferFormOpen, setIsTransferFormOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTransfer, setSelectedTransfer] = useState<Transfer | null>(null);

  const queryClient = useQueryClient();

  // Query parameters for transfers
  const transferParams: TransferListParams = {
    skip: page * rowsPerPage,
    limit: rowsPerPage,
    account_id: accountFilter,
  };

  // Fetch transfers
  const { 
    data: transfersData, 
    isLoading: transfersLoading, 
    error: transfersError,
    refetch: refetchTransfers 
  } = useQuery({
    queryKey: ['transfers', transferParams],
    queryFn: () => transfersApi.getTransfers(transferParams),
    refetchInterval: 5000, // Auto-refresh every 5 seconds like accounts
  });

  // Fetch accounts for filter dropdown and transfer form
  const { 
    data: accountsData, 
    isLoading: accountsLoading 
  } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => accountsApi.getAccounts(),
    refetchInterval: 5000,
  });

  const transfers = transfersData?.items || [];
  const totalCount = transfersData?.total || 0;
  const accounts = accountsData?.items || [];

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleAccountFilterChange = (accountId: number | '') => {
    setAccountFilter(accountId === '' ? undefined : accountId);
    setPage(0);
  };

  const handleCreateTransfer = async (transferData: TransferCreate) => {
    await transfersApi.createTransfer(transferData);
    setIsTransferFormOpen(false);
    refetchTransfers();
  };

  const handleEditTransfer = (transfer: Transfer) => {
    setSelectedTransfer(transfer);
    setIsEditDialogOpen(true);
  };

  const handleUpdateTransfer = async (updateData: TransferUpdate) => {
    if (!selectedTransfer) return;
    
    await transfersApi.updateTransfer(selectedTransfer.id, updateData);
    setIsEditDialogOpen(false);
    setSelectedTransfer(null);
    
    // Invalidate and refetch transfers
    queryClient.invalidateQueries({ queryKey: ['transfers'] });
  };

  const handleDeleteTransfer = (transfer: Transfer) => {
    setSelectedTransfer(transfer);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedTransfer) return;
    
    await transfersApi.deleteTransfer(selectedTransfer.id);
    setIsDeleteDialogOpen(false);
    setSelectedTransfer(null);
    
    // Invalidate and refetch transfers
    queryClient.invalidateQueries({ queryKey: ['transfers'] });
  };

  const getAccountName = (accountId: number): string => {
    const account = accounts.find(acc => acc.id === accountId);
    return account ? account.name : `Account ${accountId}`;
  };

  const formatCurrency = (amount: number, currency: string): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (transfersError) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load transfers. Please try again.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          <SwapHorizIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
          Transfers
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsTransferFormOpen(true)}
          sx={{ borderRadius: 2 }}
        >
          New Transfer
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
              disabled={accountsLoading}
            >
              <MenuItem value="">
                <em>All Accounts</em>
              </MenuItem>
              {accounts.map((account) => (
                <MenuItem key={account.id} value={account.id}>
                  {account.name} ({account.currency})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </Paper>

      {/* Transfers Table */}
      <Paper sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'grey.50' }}>
                <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>From Account</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>To Account</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Exchange Rate</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
                <TableCell sx={{ fontWeight: 600, width: 120 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transfersLoading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : transfers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      No transfers found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                transfers.map((transfer: Transfer) => (
                  <TableRow key={transfer.id} hover>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(transfer.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getAccountName(transfer.from_account_id)}
                        variant="outlined"
                        size="small"
                        color="error"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getAccountName(transfer.to_account_id)}
                        variant="outlined"
                        size="small"
                        color="success"
                      />
                    </TableCell>
                    <TableCell>
                      <Stack spacing={0.5}>
                        <Typography variant="body2" color="error.main">
                          -{formatCurrency(transfer.from_amount, transfer.from_currency)}
                        </Typography>
                        <Typography variant="body2" color="success.main">
                          +{formatCurrency(transfer.to_amount, transfer.to_currency)}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      {transfer.exchange_rate ? (
                        <Typography variant="body2" color="text.secondary">
                          {transfer.exchange_rate.toFixed(4)}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {transfer.description || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={0.5}>
                        <Tooltip title="Edit transfer">
                          <IconButton
                            size="small"
                            onClick={() => handleEditTransfer(transfer)}
                            sx={{ color: 'primary.main' }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete transfer">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteTransfer(transfer)}
                            sx={{ color: 'error.main' }}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
          sx={{ borderTop: 1, borderColor: 'divider' }}
        />
      </Paper>

      {/* Transfer Form Dialog */}
      <TransferForm
        open={isTransferFormOpen}
        onClose={() => setIsTransferFormOpen(false)}
        onSubmit={handleCreateTransfer}
        accounts={accounts}
      />

      {/* Edit Transfer Dialog */}
      <EditTransferDialog
        open={isEditDialogOpen}
        onClose={() => {
          setIsEditDialogOpen(false);
          setSelectedTransfer(null);
        }}
        onSubmit={handleUpdateTransfer}
        transfer={selectedTransfer}
        accounts={accounts}
      />

      {/* Delete Transfer Dialog */}
      <DeleteTransferDialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setSelectedTransfer(null);
        }}
        onConfirm={handleConfirmDelete}
        transfer={selectedTransfer}
        getAccountName={getAccountName}
      />

      {/* Floating Action Button - Alternative placement */}
      <Fab
        color="primary"
        aria-label="add transfer"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', sm: 'none' }, // Only show on mobile
        }}
        onClick={() => setIsTransferFormOpen(true)}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default TransfersPage;