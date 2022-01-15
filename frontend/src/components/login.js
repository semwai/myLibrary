import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Form, Button } from 'react-bootstrap';
import './login.css';

async function loginUser(credentials) {
  let res = await fetch(`${process.env.REACT_APP_BACK_ADDR}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentials)
  })
  
     
  let data = await res.json()
  
  if (!res.ok)
    throw new Error(data.detail)
  return data
}

export default function Login({ setToken }) {
  const [username, setUserName] = useState();
  const [password, setPassword] = useState();

  const handleSubmit = async e => {
    e.preventDefault();
    
    try {
      const token = await loginUser({
        username,
        password
      });
      setToken(token);
    } catch (e){
      alert(e.message)
    }
  }

  return (
    <div className="login-wrapper">
      <h1>Please Log In</h1>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="formName">
          <Form.Label>Book name</Form.Label>
          <Form.Control type="username" required placeholder="Enter book name" onChange={e => setUserName(e.target.value)} />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formAuthor">
          <Form.Label>Book author</Form.Label>
          <Form.Control type="password" placeholder="Enter book author" onChange={e => setPassword(e.target.value)} />
        </Form.Group>
        <Button variant="primary" type="submit">
          Login
        </Button>
      </Form>
    </div>
  )
}

Login.propTypes = {
  setToken: PropTypes.func.isRequired
}