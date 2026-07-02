const QUEUE_PREFIX = 'untold-offline-queue:';

let storage = {
  async getItem() {
    return null;
  },
  async setItem() {},
};

export function configureOfflineStore(store) {
  storage = store;
}

async function readQueue(name) {
  const raw = await storage.getItem(QUEUE_PREFIX + name);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

async function writeQueue(name, items) {
  await storage.setItem(QUEUE_PREFIX + name, JSON.stringify(items));
}

export async function enqueue(name, item) {
  const queue = await readQueue(name);
  queue.push({ ...item, _queued_at: Date.now(), _id: `${Date.now()}-${Math.random().toString(36).slice(2)}` });
  await writeQueue(name, queue);
  return queue.length;
}

export async function peekQueue(name) {
  return readQueue(name);
}

export async function flushQueue(name, handler) {
  const queue = await readQueue(name);
  if (!queue.length) return { flushed: 0, failed: 0 };
  const remaining = [];
  let flushed = 0;
  let failed = 0;
  for (const item of queue) {
    try {
      await handler(item);
      flushed += 1;
    } catch {
      remaining.push(item);
      failed += 1;
    }
  }
  await writeQueue(name, remaining);
  return { flushed, failed, remaining: remaining.length };
}

export async function getOfflineStatus(manifest, lastSyncAt) {
  const stale =
    !lastSyncAt || Date.now() - lastSyncAt > (manifest?.sync_interval_seconds ?? 300) * 1000;
  return { stale, lastSyncAt: lastSyncAt ?? null };
}

export async function syncOfflineQueues(manifest, handlers) {
  const results = {};
  for (const name of manifest?.queues ?? []) {
    if (handlers[name]) {
      results[name] = await flushQueue(name, handlers[name]);
    }
  }
  return results;
}
