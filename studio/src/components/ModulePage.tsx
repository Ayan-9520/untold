import { type ReactNode } from 'react';
import { Card, CardTitle } from '@/components/ui/card';

export default function ModulePage({ title, description, children }: { title: string; description: string; children?: ReactNode }) {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold tracking-[0.25em] text-studio-gold uppercase">UNTOLD Studio</p>
        <h1 className="text-2xl font-bold text-white mt-1">{title}</h1>
        <p className="text-sm text-studio-muted mt-1">{description}</p>
      </div>
      {children || (
        <Card>
          <CardTitle>Connected to Studio Platform API</CardTitle>
          <p className="text-sm text-studio-muted mt-2">Module routes are registered. Extend via /api/v1/studio/platform endpoints.</p>
        </Card>
      )}
    </div>
  );
}
