import React, { useEffect, useState } from 'react';
import { NavigationContainer, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { bootstrapOriginalsApp } from './src/lib/bootstrap';
import HomeScreen from './src/screens/HomeScreen';
import WatchlistScreen from './src/screens/WatchlistScreen';
import AccountScreen from './src/screens/AccountScreen';
import PlayerScreen from './src/screens/PlayerScreen';

const Tab = createBottomTabNavigator();
const HomeStack = createNativeStackNavigator();
const WatchlistStack = createNativeStackNavigator();

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

const stackScreenOptions = {
  headerStyle: { backgroundColor: '#0a0a0a' },
  headerTintColor: '#fafafa',
};

function HomeNavigator() {
  return (
    <HomeStack.Navigator screenOptions={stackScreenOptions}>
      <HomeStack.Screen name="HomeFeed" component={HomeScreen} options={{ title: 'Originals' }} />
      <HomeStack.Screen name="Player" component={PlayerScreen} options={{ title: 'Player' }} />
    </HomeStack.Navigator>
  );
}

function WatchlistNavigator() {
  return (
    <WatchlistStack.Navigator screenOptions={stackScreenOptions}>
      <WatchlistStack.Screen name="WatchlistFeed" component={WatchlistScreen} />
      <WatchlistStack.Screen name="Player" component={PlayerScreen} options={{ title: 'Player' }} />
    </WatchlistStack.Navigator>
  );
}

export default function App() {
  const [apis, setApis] = useState(null);

  useEffect(() => {
    const ctx = bootstrapOriginalsApp({ onUnauthorized: () => {} });
    setApis(ctx);
  }, []);

  if (!apis) return null;

  return (
    <NavigationContainer theme={theme}>
      <StatusBar style="light" />
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarStyle: { backgroundColor: '#171717', borderTopColor: '#262626' },
          tabBarActiveTintColor: '#e11d48',
          tabBarInactiveTintColor: '#737373',
        }}
      >
        <Tab.Screen name="Home" component={HomeNavigator} />
        <Tab.Screen name="Watchlist" component={WatchlistNavigator} />
        <Tab.Screen name="Account">
          {() => <AccountScreen authApi={apis.authApi} />}
        </Tab.Screen>
      </Tab.Navigator>
    </NavigationContainer>
  );
}
