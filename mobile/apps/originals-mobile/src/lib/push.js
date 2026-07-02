import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { mobileApi } from '@untold/api';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

export async function registerPushToken() {
  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;
  if (existing !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') return null;

  const tokenData = await Notifications.getExpoPushTokenAsync();
  const token = tokenData.data;
  await mobileApi.registerDevice({
    app_type: 'originals',
    platform: Platform.OS === 'ios' ? 'ios' : 'android',
    device_token: token,
    device_name: `${Platform.OS} device`,
    push_enabled: true,
    meta: { source: 'expo' },
  });
  return token;
}
