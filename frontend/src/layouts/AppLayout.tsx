import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  useTheme,
  Tabs,
  Tab,
} from '@mui/material';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { Link, useLocation } from '@tanstack/react-router';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const location = useLocation();

  // Determine current tab based on pathname
  const currentTab = location.pathname === '/transfers' ? 1 : 0;

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
          </Tabs>
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
    </Box>
  );
};

export default AppLayout;