import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
} from '@mui/material';
import { Currency } from '../types/account';

// Define type locally to avoid Vite import issue
interface UserSettings {
  id: number;
  default_currency: Currency;
  created_at: string;
  updated_at: string;
}

interface SettingsDialogProps {
  open: boolean;
  onClose: () => void;
  settings: UserSettings | undefined;
  onSave: (currency: Currency) => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({
  open,
  onClose,
  settings,
  onSave,
}) => {
  const [defaultCurrency, setDefaultCurrency] = useState<Currency>(Currency.USD);

  useEffect(() => {
    if (settings) {
      setDefaultCurrency(settings.default_currency);
    }
  }, [settings]);

  const handleSave = () => {
    onSave(defaultCurrency);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Settings</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Choose your preferred currency for displaying total balances and conversions.
          </Typography>
          <FormControl fullWidth>
            <InputLabel>Default Currency</InputLabel>
            <Select
              value={defaultCurrency}
              label="Default Currency"
              onChange={(e) => setDefaultCurrency(e.target.value as Currency)}
            >
              <MenuItem value={Currency.USD}>USD - US Dollar</MenuItem>
              <MenuItem value={Currency.EUR}>EUR - Euro</MenuItem>
              <MenuItem value={Currency.RUB}>RUB - Russian Ruble</MenuItem>
              <MenuItem value={Currency.JPY}>JPY - Japanese Yen</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SettingsDialog;