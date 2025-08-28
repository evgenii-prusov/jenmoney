import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Fab,
  Alert,
  Skeleton,
  Paper,
  Button,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { AccountCard } from '../../components/AccountCard';
import { AccountForm } from '../../components/AccountForm';
import { TransferForm } from '../../components/TransferForm';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { TotalBalance } from '../../components/TotalBalance';
import {
  useAccountsWithToast,
  useCreateAccountWithToast,
  useUpdateAccountWithToast,
  useDeleteAccountWithToast,
} from '../../hooks/useAccountsWithToast';
import { useCreateTransferWithToast } from '../../hooks/useTransfersWithToast';
import { useTotalBalance } from '../../hooks/useSettings';
import type { Account, AccountCreate, AccountUpdate } from '../../types/account';
import type { TransferCreate } from '../../types/transfer';

export const AccountsPage: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState<Account | null>(null);
  const [transferFormOpen, setTransferFormOpen] = useState(false);

  const { data, isLoading, error } = useAccountsWithToast();
  const createMutation = useCreateAccountWithToast();
  const updateMutation = useUpdateAccountWithToast();
  const deleteMutation = useDeleteAccountWithToast();
  const createTransferMutation = useCreateTransferWithToast();
  const { data: totalBalanceData, isLoading: totalBalanceLoading } = useTotalBalance();

  const handleCreateClick = () => {
    setFormMode('create');
    setSelectedAccount(null);
    setFormOpen(true);
  };

  const handleTransferClick = () => {
    setTransferFormOpen(true);
  };

  const handleEditClick = (account: Account) => {
    setFormMode('edit');
    setSelectedAccount(account);
    setFormOpen(true);
  };

  const handleDeleteClick = (account: Account) => {
    setAccountToDelete(account);
    setDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (formData: AccountCreate | AccountUpdate) => {
    if (formMode === 'create') {
      await createMutation.mutateAsync(formData as AccountCreate);
    } else if (selectedAccount) {
      await updateMutation.mutateAsync({
        id: selectedAccount.id,
        data: formData as AccountUpdate,
      });
    }
  };

  const handleDeleteConfirm = async () => {
    if (accountToDelete) {
      try {
        await deleteMutation.mutateAsync(accountToDelete.id);
        setDeleteDialogOpen(false);
        setAccountToDelete(null);
      } catch (error) {
        console.error('Failed to delete account:', error);
      }
    }
  };

  const handleTransferSubmit = async (transferData: TransferCreate) => {
    await createTransferMutation.mutateAsync(transferData);
  };


  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load accounts. Please try again later.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
            My Accounts
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your financial accounts and track balances
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {data && data.items.length >= 2 && (
            <Button
              variant="outlined"
              startIcon={<SwapHorizIcon />}
              onClick={handleTransferClick}
              sx={{ mr: 1 }}
            >
              Transfer
            </Button>
          )}
        </Box>
      </Box>

      {!isLoading && data && data.items.length > 0 && (
        <TotalBalance data={totalBalanceData} loading={totalBalanceLoading} />
      )}

      <Grid container spacing={3}>
        {isLoading ? (
          // Loading skeletons
          Array.from({ length: 6 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Skeleton
                variant="rounded"
                height={180}
                sx={{ borderRadius: 3 }}
              />
            </Grid>
          ))
        ) : data && data.items.length > 0 ? (
          // Account cards
          data.items.map((account) => (
            <Grid item xs={12} sm={6} md={4} key={account.id}>
              <AccountCard
                account={account}
                onEdit={handleEditClick}
                onDelete={handleDeleteClick}
              />
            </Grid>
          ))
        ) : (
          // Empty state
          <Grid item xs={12}>
            <Paper
              sx={{
                p: 6,
                textAlign: 'center',
                backgroundColor: 'background.default',
                border: '2px dashed',
                borderColor: 'divider',
              }}
            >
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No accounts yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Create your first account to start tracking your finances
              </Typography>
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add account"
        onClick={handleCreateClick}
        sx={{
          position: 'fixed',
          bottom: 32,
          right: 32,
        }}
      >
        <AddIcon />
      </Fab>

      {/* Account Form Modal */}
      <AccountForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        account={selectedAccount}
        mode={formMode}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Account"
        message={`Are you sure you want to delete "${accountToDelete?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setDeleteDialogOpen(false);
          setAccountToDelete(null);
        }}
        isDestructive
      />

      {/* Transfer Form Modal */}
      <TransferForm
        open={transferFormOpen}
        onClose={() => setTransferFormOpen(false)}
        onSubmit={handleTransferSubmit}
        accounts={data?.items || []}
      />
    </Box>
  );
};

export default AccountsPage;