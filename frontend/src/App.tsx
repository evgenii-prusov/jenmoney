import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { AppLayout } from './layouts/AppLayout';
import { AccountsPage } from './features/accounts/AccountsPage';
// import { AccountsPageSafe as AccountsPage } from './features/accounts/AccountsPageSafe';
// import { AccountsPageDebug as AccountsPage } from './features/accounts/AccountsPageDebug';
import { ErrorBoundary } from './components/ErrorBoundary';
import { theme } from './theme/solarizedLight';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          autoHideDuration={3000}
        >
          <ErrorBoundary>
            <AppLayout>
              <AccountsPage />
            </AppLayout>
          </ErrorBoundary>
        </SnackbarProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;