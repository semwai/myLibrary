import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Row, Col } from 'react-bootstrap';
import useToken from '../useToken';
import './book.css'

function getPage(token, setPageUrl, setPage, book, page) {

  let path = `${process.env.REACT_APP_BACK_ADDR}/page/${book}`
  if (page != null) {
    console.log(page)
    if (page < 0)
      return
    path += `?page=${page}`
  }
  fetch(path, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}`, 'page': '' }
  })
    .then(function (response) {
      if (response.status == 404)
        throw new Error(response.statusText);
      const page = parseInt(response.headers.get('page'))
      setPage(page)
      return response.blob()
    })
    .then(function (blob) {
      var objectURL = URL.createObjectURL(blob)
      setPageUrl(objectURL)
      window.scrollTo({
        top: 0,
        behavior: "instant"
      });
    })
}

function getBookInfo(token, setbookMeta, book) {
  let path = `${process.env.REACT_APP_BACK_ADDR}/book_info/${book}`
  fetch(path, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}`, 'page': '' }
  })
    .then(res => res.json())
    .then(function (json) {
      setbookMeta(json)
      document.title = json.name + (json.author == undefined ? '': ' - ') + (json?.author || '')
    })
}

export default function Book() {

  const { token, setToken } = useToken()
  const [pageUrl, setPageUrl] = useState('#')
  const [page, setPage] = useState(undefined)
  const [bookMeta, setbookMeta] = useState(undefined)
  const book_id = useParams().id

  useEffect(() => {
    getPage(token, setPageUrl, setPage, book_id)
    getBookInfo(token, setbookMeta, book_id)
  }, [])

  return (
    <div>

      <p><img width='100%' src={pageUrl} /></p>
      <Container fluid>
        <Row>
          {page > 0 ?
            <Col className='button-center element-center' onClick={() => { getPage(token, setPageUrl, setPage, book_id, page - 1) }}>
              Back
            </Col>
            : <Col></Col>
          }
          <Col className='element-center'>{ page } of { bookMeta?.pages }</Col>
          {page + 1 < bookMeta?.pages ?
            <Col className='button-center element-center' onClick={() => { getPage(token, setPageUrl, setPage, book_id, page + 1) }}>
              Next
            </Col>
            : <Col></Col>
          }
        </Row>
      </Container>
    </div>
  )
}