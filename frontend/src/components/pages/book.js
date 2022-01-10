import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import useToken from '../useToken';

function getPage(token, setter, book) {
  fetch(`http://localhost:8000/page/${book}`, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(res => res.blob())
  .then(function (response) {
    console.log(response)
    var objectURL = URL.createObjectURL(response)
    setter(objectURL)
    console.log(objectURL)
  })
}

export default function Book() {

  const { token, setToken } = useToken();
  const [page, setPage] = useState('');
  const book_id = useParams().id

  useEffect(() => {
    getPage(token, setPage, book_id)
    
  }, []);

  return (
    <div>

       <p><img src={ page }/></p>
    </div>
  );
}