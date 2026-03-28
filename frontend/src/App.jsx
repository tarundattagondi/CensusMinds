import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Loading from './pages/Loading';
import Results from './pages/Results';
import History from './pages/History';
import Login from './pages/Login';

function ProtectedRoute({ children }) {
  const password = localStorage.getItem('censusminds_password');
  if (!password) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Landing /></ProtectedRoute>} />
        <Route path="/loading" element={<ProtectedRoute><Loading /></ProtectedRoute>} />
        <Route path="/results/:id" element={<Results />} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
