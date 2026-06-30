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
      { to: studioPath('projects'), icon: FilmIcon, label: 'Projects' },
      { to: studioPath('collaboration'), icon: UsersIcon, label: 'Collaboration' },
      { to: studioPath('ai-cost'), icon: DollarSignIcon, label: 'AI Cost Optimization' },
      { to: studioPath('marketplace'), icon: GlobeIcon, label: 'Agent Marketplace' },
      { to: studioPath('plugins'), icon: BookIcon, label: 'Plugin Marketplace' },
      { to: studioPath('api-gateway'), icon: GlobeIcon, label: 'API Gateway' },
      { to: studioPath('security'), icon: UsersIcon, label: 'Enterprise Security' },
      { to: studioPath('workflows'), icon: FilmIcon, label: 'Workflow Engine' },
      { to: studioPath('pipeline'), icon: FilmIcon, label: 'Quick Pipeline' },
      { to: studioPath('research'), icon: GlobeIcon, label: 'Research' },
      { to: studioPath('scripts'), icon: FilmIcon, label: 'Scripts' },
      { to: studioPath('storyboard'), icon: FilmIcon, label: 'Storyboard' },
      { to: studioPath('assets'), icon: BookIcon, label: 'Asset Library' },
      { to: studioPath('timeline'), icon: FilmIcon, label: 'Timeline Editor' },
      { to: studioPath('ai'), icon: GlobeIcon, label: 'AI Studio' },
      { to: studioPath('images'), icon: GlobeIcon, label: 'Image Studio' },
      { to: studioPath('videos'), icon: FilmIcon, label: 'Video Studio' },
      { to: studioPath('voice'), icon: GlobeIcon, label: 'Voice Studio' },
      { to: studioPath('music'), icon: FilmIcon, label: 'Music Studio' },
      { to: studioPath('shorts'), icon: FilmIcon, label: 'Shorts Generator' },
      { to: studioPath('seo'), icon: GlobeIcon, label: 'SEO Studio' },
      { to: studioPath('translation'), icon: GlobeIcon, label: 'Translation Studio' },
      { to: studioPath('publishing-agent'), icon: FilmIcon, label: 'Publishing Agent' },
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
      { to: studioPath('admin'), icon: UsersIcon, label: 'Admin Panel' },
      { to: studioPath('users'), icon: UsersIcon, label: 'Team & Users' },
      { to: studioPath('notifications'), icon: BellIcon, label: 'Notifications' },
    ],
  },
];
