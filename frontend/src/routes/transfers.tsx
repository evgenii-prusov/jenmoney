import { createFileRoute } from '@tanstack/react-router'
import { TransfersPage } from '../features/transfers/TransfersPage'

export const Route = createFileRoute('/transfers')({
  component: TransfersPage,
})