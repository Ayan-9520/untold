import React, { useEffect, useState } from 'react';
import { NavigationContainer, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { isAuthenticated } from '@untold/auth';
import { bootstrapStudioApp } from './src/lib/bootstrap';
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import ApprovalsScreen from './src/screens/ApprovalsScreen';
import AiJobsScreen from './src/screens/AiJobsScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import UploadScreen from './src/screens/UploadScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();

const theme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: '#0a0a0a',
    card: '#171717',
    primary: '#e11d48',
    border: '#262626',
  },
};

export default function App() {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [apis, setApis] = useState(null);

  useEffect(() => {
    const ctx = bootstrapStudioApp({
      onUnauthorized: () => setAuthed(false),
    });
    setApis(ctx);
    isAuthenticated().then((ok) => {
      setAuthed(ok);
      setReady(true);
    });
  }, []);

  if (!ready || !apis) return null;

  if (!authed) {
    return (
      <>
        <StatusBar style="light" />
        <LoginScreen authApi={apis.authApi} onLoggedIn={() => setAuthed(true)} />
      </>
    );
  }

  return (
    <NavigationContainer theme={theme}>
      <StatusBar style="light" />
      <Tab.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#0a0a0a' },
          headerTintColor: '#fafafa',
          tabBarStyle: { backgroundColor: '#171717', borderTopColor: '#262626' },
          tabBarActiveTintColor: '#e11d48',
          tabBarInactiveTintColor: '#737373',
        }}
      >
        <Tab.Screen name="Dashboard" component={DashboardScreen} />
        <Tab.Screen name="Approvals" component={ApprovalsScreen} />
        <Tab.Screen name="AI Jobs" component={AiJobsScreen} />
        <Tab.Screen name="Analytics" component={AnalyticsScreen} />
        <Tab.Screen name="Upload" component={UploadScreen} />
        <Tab.Screen name="Settings">
          {() => <SettingsScreen onLogout={() => setAuthed(false)} />}
        </Tab.Screen>
      </Tab.Navigator>
    </NavigationContainer>
  );
}
