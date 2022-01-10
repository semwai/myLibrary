import React, { useState, useEffect, useCallback } from 'react';
import useToken from '../useToken';

function getBooks(token, setter) {
  fetch('http://localhost:8000/books', {
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
    console.log(books)
  }, []);
  

  
  return (
    <div>
      <h2>Books</h2>
      <ul>
        {books.map(book => <li key={book.id}>{book.name} {book.author?' - ' + book.author:''}</li>)}
      </ul>
    </div>
  );
}