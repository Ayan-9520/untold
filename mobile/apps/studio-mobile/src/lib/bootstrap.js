import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';
import { configureApi, authApi, mobileApi } from '@untold/api';
import { configureAuthStore, getAccessToken, clearSession } from '@untold/auth';
import { configureOfflineStore } from '@untold/offline';

const secureStore = {
  getItem: (k) => SecureStore.getItemAsync(k),
  setItem: (k, v) => SecureStore.setItemAsync(k, v),
  removeItem: (k) => SecureStore.deleteItemAsync(k),
};

export function bootstrapStudioApp({ onUnauthorized }) {
  configureAuthStore(secureStore);
  configureOfflineStore(AsyncStorage);

  const apiUrl = Constants.expoConfig?.extra?.apiUrl ?? 'http://localhost:8000/api/v1';
  configureApi({
    baseUrl: apiUrl,
    tokenProvider: getAccessToken,
    unauthorizedHandler: onUnauthorized ?? (() => clearSession()),
  });

  return { authApi, mobileApi, apiUrl };
}
