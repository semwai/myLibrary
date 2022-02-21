import React from 'react'
import useToken from '../../useToken'
import { useState, useEffect } from 'react';

function getActivity(token, setActivity) {
  fetch(`${process.env.REACT_APP_BACK_ADDR}/activity`, {
    mode: 'cors',
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(res => res.json())
    .then(data => {
      setActivity(data)
      console.log(data)
    })
}

export default function Index() {
  const { token } = useToken()
  const [activity, setActivity] = useState([])

  useEffect(() => {
    getActivity(token, setActivity)
  }, []);

  return (<div>
    <h1>User activity:</h1>
    <ul>
      {activity.map((e, i) => (<li>{e.date} - {e.pages}</li>))}
    </ul>
  </div>);
}