import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  useTheme,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import SettingsIcon from '@mui/icons-material/Settings';
import { Link, useLocation } from '@tanstack/react-router';
import { SettingsDialog } from '../components/SettingsDialog';
import { useSettings, useUpdateSettings } from '../hooks/useSettings';
import type { Currency } from '../types/account';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const location = useLocation();
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Settings hooks
  const { data: settings } = useSettings();
  const updateSettings = useUpdateSettings();

  // Determine current tab based on pathname
  const getCurrentTab = () => {
    if (location.pathname === '/transfers') return 1;
    if (location.pathname === '/transactions') return 2;
    if (location.pathname === '/budgets') return 3;
    return 0; // Default to accounts
  };
  
  const currentTab = getCurrentTab();

  // Settings handler
  const handleSettingsSave = async (currency: Currency) => {
    await updateSettings.mutateAsync({ default_currency: currency });
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          backgroundColor: 'background.paper',
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Toolbar>
          <AccountBalanceWalletIcon
            sx={{
              mr: 2,
              color: 'primary.main',
              fontSize: 32,
            }}
          />
          <Typography
            variant="h5"
            component="h1"
            sx={{
              fontWeight: 600,
              color: 'text.primary',
              letterSpacing: '-0.5px',
              mr: 4,
            }}
          >
            {import.meta.env.VITE_APP_NAME || 'JenMoney'}
          </Typography>
          
          <Tabs 
            value={currentTab} 
            sx={{ 
              flexGrow: 1,
              '& .MuiTab-root': {
                color: 'text.secondary',
                fontWeight: 500,
                textTransform: 'none',
                fontSize: '1rem',
                minHeight: 48,
              },
              '& .Mui-selected': {
                color: 'primary.main',
              },
              '& .MuiTabs-indicator': {
                backgroundColor: 'primary.main',
              },
            }}
          >
            <Tab
              label="Accounts"
              icon={<AccountBalanceWalletIcon />}
              iconPosition="start"
              component={Link}
              to="/"
              sx={{
                '& .MuiTab-iconWrapper': {
                  marginRight: 1,
                  marginBottom: 0,
                },
              }}
            />
            <Tab
              label="Transfers"
              icon={<SwapHorizIcon />}
              iconPosition="start"
              component={Link}
              to="/transfers"
              sx={{
                '& .MuiTab-iconWrapper': {
                  marginRight: 1,
                  marginBottom: 0,
                },
              }}
            />
            <Tab
              label="Transactions"
              icon={<ReceiptIcon />}
              iconPosition="start"
              component={Link}
              to="/transactions"
              sx={{
                '& .MuiTab-iconWrapper': {
                  marginRight: 1,
                  marginBottom: 0,
                },
              }}
            />
            <Tab
              label="Budgets"
              icon={<AccountBalanceIcon />}
              iconPosition="start"
              component={Link}
              to="/budgets"
              sx={{
                '& .MuiTab-iconWrapper': {
                  marginRight: 1,
                  marginBottom: 0,
                },
              }}
            />
          </Tabs>
          
          {/* Global Settings Button */}
          <Tooltip title="Settings">
            <IconButton
              onClick={() => setSettingsOpen(true)}
              sx={{ 
                color: 'text.secondary',
                '&:hover': {
                  color: 'primary.main',
                },
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          backgroundColor: 'background.default',
          py: 4,
        }}
      >
        <Container maxWidth="lg">{children}</Container>
      </Box>

      {/* Global Settings Dialog */}
      <SettingsDialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        settings={settings}
        onSave={handleSettingsSave}
      />
    </Box>
  );
};

export default AppLayout;