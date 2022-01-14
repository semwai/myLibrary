import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button, ListGroup, Modal, Form } from 'react-bootstrap';
import useToken from '../useToken';
import './books.css'
import Loader from '../loader';

function getBooks(token, setBooks, setWait) {
  setWait(true)
  fetch(`${process.env.REACT_APP_BACK_ADDR}/books`, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(res => res.json())
    .then(data => {
      setBooks(data.books)
      setWait(false)
    })
}

export default function Books() {
  const { token } = useToken();
  const [books, setBooks] = useState([]);
  // modal variables
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  // form data 
  const [name, setName] = useState();
  const [author, setAuthor] = useState();
  const [file, setFile] = useState();
  // wait for request 
  const [wait, setWait] = useState(false)

  useEffect(() => {
    getBooks(token, setBooks, setWait)
  }, []);

  const postBook = async e => {
    e.preventDefault();
    //console.log(name, author, file)
    let path = `${process.env.REACT_APP_BACK_ADDR}/book?name=${name}`
    if (author !== undefined)
      path += `&author=${author}`
    let data = new FormData()
    data.append('file', file)
    fetch(path, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`},
      body: data
    }).then(res => res.json())
      .then(json => {
        handleClose()
        getBooks(token, setBooks, setWait)
      })
  }

  if (wait)
    return <Loader/>

  return (
    <div>
      <h2>Books </h2>
      <ListGroup>
        {books.map(book =>
          <Link key={book.id} to={'/book/' + book.id}>
            <ListGroup.Item variant="dark">
              {book.name} {book.author ? ' - ' + book.author : ''}
            </ListGroup.Item>
          </Link>)}
      </ListGroup>
      <div className='add-book-wrapper'>
        <Button variant="success" onClick={handleShow}>Add book</Button>
      </div>

      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Enter book info</Modal.Title>
        </Modal.Header>
        <Modal.Body>

          <Form onSubmit={postBook}>
            <Form.Group className="mb-3" controlId="formName">
              <Form.Label>Book name</Form.Label>
              <Form.Control type="text" required placeholder="Enter book name" onChange={e => setName(e.target.value)} />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formAuthor">
              <Form.Label>Book author</Form.Label>
              <Form.Control type="text" placeholder="Enter book author" onChange={e => setAuthor(e.target.value)}/>
            </Form.Group>
            <Form.Group controlId="formFile" className="mb-3">
              <Form.Label>PDF file</Form.Label>
              <Form.Control required type="file" onChange={e => setFile(e.target.files[0])}/>
            </Form.Group>
            <Button variant="primary" type="submit">
              Submit
            </Button>
          </Form>
        </Modal.Body>

      </Modal>

    </div>
  );
}