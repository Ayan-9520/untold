import { Component } from 'react';
import Button from './ui/Button';

export default class AppErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('[AppErrorBoundary]', error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4 dark:bg-untold-dark light:bg-gray-50">
          <h1 className="text-xl font-bold dark:text-untold-white light:text-black">Something went wrong</h1>
          <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600 max-w-md text-center">
            {import.meta.env.PROD ? 'Please refresh the page or try again later.' : this.state.error.message}
          </p>
          <Button className="mt-6" onClick={() => window.location.reload()}>
            Reload
          </Button>
        </div>
      );
    }
    return this.props.children;
  }
}
