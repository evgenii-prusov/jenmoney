import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createRouter, RouterProvider } from '@tanstack/react-router';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { ErrorBoundary } from './components/ErrorBoundary';
import { theme } from './theme/solarizedLight';

// Import the generated route tree
import { routeTree } from './routeTree.gen';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Create a new router instance
const router = createRouter({ routeTree });

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

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
            <RouterProvider router={router} />
          </ErrorBoundary>
        </SnackbarProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;