import React, { useCallback, useState } from 'react';
import { ScrollView, Text, View, RefreshControl } from 'react-native';
import { mobileApi } from '@untold/api';
import { enqueue } from '@untold/offline';
import { Screen, Title, Card, Muted, PrimaryButton, OfflineBanner, colors } from '../components/ui';
import { useOfflineSync, studioOfflineHandlers } from '../hooks/useOfflineSync';

export default function ApprovalsScreen() {
  const [items, setItems] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const { online, syncing, sync } = useOfflineSync('studio', studioOfflineHandlers);

  const load = useCallback(async () => {
    const rows = await mobileApi.studioApprovals();
    setItems(rows);
  }, []);

  const refresh = async () => {
    setRefreshing(true);
    try {
      await sync();
      await load();
    } finally {
      setRefreshing(false);
    }
  };

  React.useEffect(() => {
    load().catch(() => {});
  }, [load]);

  const act = async (approvalId, action) => {
    if (online) {
      await mobileApi.studioApprovalAction(approvalId, action);
      await load();
    } else {
      await enqueue('approval_actions', { approval_id: approvalId, action });
      setItems((prev) => prev.filter((x) => x.id !== approvalId));
    }
  };

  return (
    <Screen>
      <OfflineBanner online={online} syncing={syncing} />
      <ScrollView refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#e11d48" />}>
        <Title>Project approvals</Title>
        {!items.length && <Muted>No pending approvals</Muted>}
        {items.map((item) => (
          <Card key={item.id}>
            <Text style={{ color: colors.text, fontWeight: '600' }}>{item.project_title}</Text>
            <Muted>
              {item.entity_type} · project #{item.project_id}
            </Muted>
            <View style={{ flexDirection: 'row', gap: 8, marginTop: 12 }}>
              <View style={{ flex: 1 }}>
                <PrimaryButton title="Approve" onPress={() => act(item.id, 'approve')} />
              </View>
              <View style={{ flex: 1 }}>
                <PrimaryButton title="Reject" onPress={() => act(item.id, 'reject')} />
              </View>
            </View>
          </Card>
        ))}
      </ScrollView>
    </Screen>
  );
}
