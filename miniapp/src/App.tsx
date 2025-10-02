import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Listing from './pages/Listing';
import Favorites from './pages/Favorites';
import Header from './components/Header';

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/listing/:id" element={<Listing />} />
        <Route path="/favorites" element={<Favorites />} />
      </Routes>
    </Router>
  );
}

export default App;