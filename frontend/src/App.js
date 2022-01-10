import { BrowserRouter, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import Book from './components/pages/book';
import Books from './components/pages/books';
import Index from './components/pages/Index';
import Login from './components/login';
import useToken from './components/useToken';


function App() {
  const { token, setToken } = useToken();

  if (!token) {
    return <Login setToken={setToken} />
  }

  return (
      <BrowserRouter>
        <div>
          <nav>
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/book">book</Link>
              </li>
              <li>
                <Link to="/books">books</Link>
              </li>
            </ul>
          </nav>
          <Routes>
            <Route path="/" element={<Index />}>
            </Route>
            <Route path="/book/:id" element={<Book />}>
            </Route>
            <Route path="/books" element={<Books />}>
            </Route>
          </Routes>
        </div>
      </BrowserRouter>
  );
}


export default App;
