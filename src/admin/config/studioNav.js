import {
  LayoutDashboardIcon,
  UsersIcon,
  FilmIcon,
  BarChartIcon,
  DollarSignIcon,
  BellIcon,
  GlobeIcon,
  CreditCardIcon,
  BookIcon,
} from '../components/AdminIcons';
import { studioPath } from '../../config/ecosystem';

/** UNTOLD STUDIO sidebar — single source for internal nav */
export const STUDIO_NAV = [
  {
    title: 'Overview',
    items: [
      { to: studioPath(), icon: LayoutDashboardIcon, label: 'Dashboard', end: true },
      { to: studioPath('ecosystem'), icon: GlobeIcon, label: 'Ecosystem Map' },
    ],
  },
  {
    title: 'Produce',
    items: [
      { to: studioPath('research'), icon: GlobeIcon, label: 'Research' },
      { to: studioPath('scripts'), icon: FilmIcon, label: 'Scripts' },
      { to: studioPath('assets'), icon: BookIcon, label: 'Asset Library' },
      { to: studioPath('ai'), icon: GlobeIcon, label: 'AI Agents' },
      { to: studioPath('content'), icon: FilmIcon, label: 'Publishing CMS' },
      { to: studioPath('ai-localization'), icon: GlobeIcon, label: 'Localization' },
      { to: studioPath('magazine'), icon: BookIcon, label: 'E-Magazine' },
      { to: studioPath('team'), icon: UsersIcon, label: 'Human & AI Team' },
    ],
  },
  {
    title: 'Originals feedback',
    items: [
      { to: studioPath('analytics'), icon: BarChartIcon, label: 'Viewer Analytics' },
      { to: studioPath('membership'), icon: CreditCardIcon, label: 'Subscriptions' },
      { to: studioPath('revenue'), icon: DollarSignIcon, label: 'Revenue' },
    ],
  },
  {
    title: 'Operations',
    items: [
      { to: studioPath('users'), icon: UsersIcon, label: 'Team & Users' },
      { to: studioPath('notifications'), icon: BellIcon, label: 'Notifications' },
    ],
  },
];
