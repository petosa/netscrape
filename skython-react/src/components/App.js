import React, { Component } from 'react';
import WindowLayout from './WindowLayout.js'
import logo from './res/logo.svg';
import './style/App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
        </div>
        <WindowLayout/>
      </div>
    );
  }
}

export default App;
