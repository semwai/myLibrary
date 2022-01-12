import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ListGroup } from 'react-bootstrap';
import useToken from '../useToken';

function getBooks(token, setter) {
  fetch(`${process.env.REACT_APP_BACK_ADDR}/books`, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(res => res.json())
    .then(data => setter(data.books))
}

export default function Books() {
  const { token, setToken } = useToken();
  const [books, setBooks] = useState([]);


  useEffect(() => {
    getBooks(token, setBooks)
  }, []);


  return (
    <div>
      <h2>Books </h2>
      <ListGroup>
        {books.map(book =>
          <Link to={'/book/' + book.id}>
            <ListGroup.Item key={book.id}>
              {book.name} {book.author ? ' - ' + book.author : ''}
            </ListGroup.Item>
          </Link>)}
      </ListGroup>
    </div>
  );
}