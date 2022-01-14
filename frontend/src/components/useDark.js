import React from "react";

const ThemeContext = React.createContext({
  dark: true, 
  setDark: (value) => {}
 })

export default ThemeContext
