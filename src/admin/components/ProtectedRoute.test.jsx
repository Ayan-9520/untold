import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';

const mockUseAdminAuth = vi.fn();

vi.mock('../context/AdminAuthContext', () => ({
  useAdminAuth: () => mockUseAdminAuth(),
}));

function renderProtected(initialPath = '/studio/dashboard') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/studio/login" element={<div>Login Page</div>} />
        <Route
          path="/studio/dashboard"
          element={
            <ProtectedRoute>
              <div>Studio Dashboard</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ProtectedRoute', () => {
  it('shows loading spinner while auth initializes', () => {
    mockUseAdminAuth.mockReturnValue({
      loading: true,
      isAuthenticated: false,
      hasStudioAccess: false,
    });

    renderProtected();
    expect(document.querySelector('.animate-spin')).toBeTruthy();
  });

  it('redirects unauthenticated users to studio login', () => {
    mockUseAdminAuth.mockReturnValue({
      loading: false,
      isAuthenticated: false,
      hasStudioAccess: false,
    });

    renderProtected();
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('renders children for authenticated studio users', () => {
    mockUseAdminAuth.mockReturnValue({
      loading: false,
      isAuthenticated: true,
      hasStudioAccess: true,
    });

    renderProtected();
    expect(screen.getByText('Studio Dashboard')).toBeInTheDocument();
  });
});
