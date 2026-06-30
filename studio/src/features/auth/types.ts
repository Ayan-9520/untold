export type StudioRole =
  | 'admin'
  | 'producer'
  | 'researcher'
  | 'writer'
  | 'editor'
  | 'designer'
  | 'publisher'
  | 'viewer';

export interface StudioUser {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_admin: boolean;
  role: string;
  studio_role: StudioRole;
  permissions: string[];
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}
