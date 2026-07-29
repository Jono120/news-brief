import { Link, Route, Routes } from "react-router";
import QueuePage from "./pages/QueuePage";
import StoryPage from "./pages/StoryPage";

export default function App() {
  return (
    <div className="app">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="app-header" role="banner">
        <Link to="/" className="brand">
          Brief APAC — review
        </Link>
      </header>
      <main id="main-content" className="app-main" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<QueuePage />} />
          <Route path="/story/:id" element={<StoryPage />} />
        </Routes>
      </main>
    </div>
  );
}
