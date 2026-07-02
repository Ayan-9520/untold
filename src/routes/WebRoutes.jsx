import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Loader from '../components/ui/Loader';
import ContactRedirect from '../components/ContactRedirect';

const Home = lazy(() => import('../pages/Home'));
const About = lazy(() => import('../pages/About'));
const Originals = lazy(() => import('../pages/Originals'));
const Hub = lazy(() => import('../pages/Hub'));
const Events = lazy(() => import('../pages/Events'));
const Live = lazy(() => import('../pages/Live'));
const LiveMatchDetail = lazy(() => import('../pages/LiveMatchDetail'));
const News = lazy(() => import('../pages/News'));
const NewsArticle = lazy(() => import('../pages/NewsArticle'));
const Legends = lazy(() => import('../pages/Legends'));
const Rivalries = lazy(() => import('../pages/Rivalries'));
const Shorts = lazy(() => import('../pages/Shorts'));
const Stories = lazy(() => import('../pages/Stories'));
const Secrets = lazy(() => import('../pages/Secrets'));
const Explore = lazy(() => import('../pages/Explore'));
const VideoDetail = lazy(() => import('../pages/VideoDetail'));
const Membership = lazy(() => import('../pages/Membership'));
const Magazine = lazy(() => import('../pages/Magazine'));
const MagazineIssue = lazy(() => import('../pages/MagazineIssue'));
const Login = lazy(() => import('../pages/Login'));
const ForgotPassword = lazy(() => import('../pages/ForgotPassword'));
const ResetPassword = lazy(() => import('../pages/ResetPassword'));
const Signup = lazy(() => import('../pages/Signup'));
const Profile = lazy(() => import('../pages/Profile'));
const Watchlist = lazy(() => import('../pages/Watchlist'));
const Blog = lazy(() => import('../pages/Blog'));
const FanWars = lazy(() => import('../pages/FanWars'));
const Predictions = lazy(() => import('../pages/Predictions'));

export default function WebRoutes() {
  return (
    <Suspense fallback={<Loader fullScreen label="Loading UNTOLD" />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/originals" element={<Originals />} />
        <Route path="/hub" element={<Hub />} />
        <Route path="/events" element={<Events />} />
        <Route path="/legends" element={<Legends />} />
        <Route path="/rivalries" element={<Rivalries />} />
        <Route path="/stories" element={<Stories />} />
        <Route path="/secrets" element={<Secrets />} />
        <Route path="/shorts" element={<Shorts />} />
        <Route path="/live" element={<Live />} />
        <Route path="/live/:id" element={<LiveMatchDetail />} />
        <Route path="/news" element={<News />} />
        <Route path="/news/:id" element={<NewsArticle />} />
        <Route path="/contact" element={<ContactRedirect />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/video/:id" element={<VideoDetail />} />
        <Route path="/membership" element={<Membership />} />
        <Route path="/magazine" element={<Magazine />} />
        <Route path="/magazine/:id" element={<MagazineIssue />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/fan-wars" element={<FanWars />} />
        <Route path="/predictions" element={<Predictions />} />
      </Routes>
    </Suspense>
  );
}
