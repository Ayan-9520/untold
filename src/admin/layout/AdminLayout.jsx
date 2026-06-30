import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { PluginProvider } from '../../plugin-sdk';
import { studioPlatform } from '../api/adminApi';

export default function AdminLayout() {
  return (
    <PluginProvider fetchRuntime={() => studioPlatform.getPluginRuntime()}>
      <div className="flex min-h-screen dark:bg-untold-dark light:bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 lg:ml-0">
          <main className="flex-1 p-4 sm:p-6 lg:p-8 pt-16 lg:pt-8 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </PluginProvider>
  );
}
