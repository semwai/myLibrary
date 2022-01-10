import React, { useState, useEffect } from 'react';
import useToken from '../useToken';

function getPage(token, setter) {
  fetch('http://localhost:8000/page/3', {
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

  useEffect(() => {
    getPage(token, setPage)
    
  }, []);

  return (
    <div>

       <p><img src={ page }/></p>
    </div>
  );
}