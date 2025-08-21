import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Fab,
  Alert,
  Skeleton,
  Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { AccountCard } from '../../components/AccountCard';
import { AccountForm } from '../../components/AccountForm';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import {
  useAccountsWithToast,
  useCreateAccountWithToast,
  useUpdateAccountWithToast,
  useDeleteAccountWithToast,
} from '../../hooks/useAccountsWithToast';
import type { Account, AccountCreate, AccountUpdate } from '../../types/account';

export const AccountsPage: React.FC = () => {
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState<Account | null>(null);

  const { data, isLoading, error } = useAccountsWithToast();
  const createMutation = useCreateAccountWithToast();
  const updateMutation = useUpdateAccountWithToast();
  const deleteMutation = useDeleteAccountWithToast();

  const handleCreateClick = () => {
    setFormMode('create');
    setSelectedAccount(null);
    setFormOpen(true);
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

  const totalBalance = data?.items.reduce((sum, account) => {
    // Convert all to EUR for total (simplified - in real app would use exchange rates)
    return sum + account.balance;
  }, 0) || 0;

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
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          My Accounts
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your financial accounts and track balances
        </Typography>
      </Box>

      {!isLoading && data && data.items.length > 0 && (
        <Paper
          sx={{
            p: 3,
            mb: 4,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}
        >
          <Typography variant="subtitle2" sx={{ opacity: 0.9, mb: 1 }}>
            Total Balance (Approximate)
          </Typography>
          <Typography variant="h3" sx={{ fontWeight: 700 }}>
            €{totalBalance.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </Typography>
        </Paper>
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
    </Box>
  );
};

export default AccountsPage;