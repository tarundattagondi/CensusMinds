import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Loading from './pages/Loading';
import Results from './pages/Results';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/loading" element={<Loading />} />
        <Route path="/results/:id" element={<Results />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
