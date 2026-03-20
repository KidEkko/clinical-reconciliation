import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ReturnProvider } from './generic/customHooks.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ReturnProvider>
      <App />
    </ReturnProvider>
  </StrictMode>,
)
