import { Routes, Route, Navigate } from 'react-router-dom';
import { AppAuthProvider } from './context/AppAuthContext';
import { WatchlistProvider } from './context/WatchlistContext';
import { AppUIProvider } from './context/AppUIContext';
import AppShell from './layout/AppShell';
import SplashScreen from './screens/SplashScreen';
import LoginScreen from './screens/LoginScreen';
import SignupScreen from './screens/SignupScreen';
import HomeScreen from './screens/HomeScreen';
import OriginalsScreen from './screens/OriginalsScreen';
import ShortsScreen from './screens/ShortsScreen';
import WatchlistScreen from './screens/WatchlistScreen';
import ProfileScreen from './screens/ProfileScreen';
import PlayerScreen from './screens/PlayerScreen';

export default function MobileApp() {
  return (
    <AppAuthProvider>
      <WatchlistProvider>
        <AppUIProvider>
          <Routes>
            <Route index element={<SplashScreen />} />
            <Route path="login" element={<LoginScreen />} />
            <Route path="signup" element={<SignupScreen />} />
            <Route path="auth" element={<LoginScreen />} />
            <Route path="watch/:id" element={<PlayerScreen />} />
            <Route element={<AppShell />}>
              <Route path="home" element={<HomeScreen />} />
              <Route path="originals" element={<OriginalsScreen />} />
              <Route path="shorts" element={<ShortsScreen />} />
              <Route path="watchlist" element={<WatchlistScreen />} />
              <Route path="profile" element={<ProfileScreen />} />
            </Route>
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </AppUIProvider>
      </WatchlistProvider>
    </AppAuthProvider>
  );
}
