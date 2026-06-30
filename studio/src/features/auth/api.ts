import client from '@/api/client';
import type { AuthTokens, LoginCredentials, StudioUser } from './types';

export const authApi = {
  login: (data: LoginCredentials) =>
    client.post<AuthTokens>('/login', data).then((r) => r.data),

  googleLogin: (idToken: string) =>
    client.post<AuthTokens>('/auth/google', { id_token: idToken }).then((r) => r.data),

  studioMe: () =>
    client.get<StudioUser>('/auth/studio/me').then((r) => r.data),

  logout: () => Promise.resolve(),
};
