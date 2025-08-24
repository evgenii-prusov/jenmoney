import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import type { Transfer, TransferUpdate } from '../types/transfer';

interface EditTransferDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: TransferUpdate) => Promise<void>;
  transfer: Transfer | null;
}

export const EditTransferDialog: React.FC<EditTransferDialogProps> = ({
  open,
  onClose,
  onSubmit,
  transfer,
}) => {
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (open && transfer) {
      setDescription(transfer.description || '');
      setSubmitError(null);
    }
  }, [open, transfer]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!transfer) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit({ description: description.trim() || null });
      onClose();
    } catch (error) {
      console.error('Failed to update transfer:', error);
      setSubmitError(error instanceof Error ? error.message : 'Failed to update transfer');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <EditIcon />
        Edit Transfer
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {submitError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {submitError}
            </Alert>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
              fullWidth
              placeholder="Optional description for this transfer"
              helperText="Note: Only the description can be edited after a transfer is created"
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Updating...' : 'Update Transfer'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default EditTransferDialog;