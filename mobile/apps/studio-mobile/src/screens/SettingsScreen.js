import React from 'react';
import { clearSession, getStoredUser } from '@untold/auth';
import { Screen, Title, Card, Muted, PrimaryButton } from '../components/ui';

export default function SettingsScreen({ onLogout }) {
  const [user, setUser] = React.useState(null);

  React.useEffect(() => {
    getStoredUser().then(setUser);
  }, []);

  const logout = async () => {
    await clearSession();
    onLogout();
  };

  return (
    <Screen>
      <Title>Settings</Title>
      <Card>
        <Muted>Signed in as</Muted>
        <Muted>{user?.email || user?.name || 'Studio user'}</Muted>
      </Card>
      <PrimaryButton title="Sign out" onPress={logout} />
    </Screen>
  );
}
