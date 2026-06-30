import { vi } from 'vitest';

export const mockAuthApi = {
  isAuthenticated: vi.fn(() => false),
  getMe: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
};

vi.mock('../../admin/api/adminApi', () => ({
  auth: mockAuthApi,
}));
