import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  useTheme,
} from '@mui/material';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const theme = useTheme();

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
              flexGrow: 1,
              fontWeight: 600,
              color: 'text.primary',
              letterSpacing: '-0.5px',
            }}
          >
            {import.meta.env.VITE_APP_NAME || 'JenMoney'}
          </Typography>
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