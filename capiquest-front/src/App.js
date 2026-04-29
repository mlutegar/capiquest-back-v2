import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Analise from './pages/Analise';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<h1>Home</h1>} />
        <Route path="/analise" element={<Analise />} />
      </Routes>
    </Router>
  );
}

export default App;