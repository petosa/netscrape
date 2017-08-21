import React, { Component } from 'react';
import TableRow from './TableRow.js';
import CodeMirror from "codemirror";
import './style/InfoPane.css';

class InfoPane extends Component {


  render() {
    
    var toDisplay = <div/>;
    var context = this.props.context;
    console.log(CodeMirror)

    if (context) {
      toDisplay =
        <div>
          <h1>Name: {context.name}</h1>
          <h1>Description: </h1> <span className="sublime">{context.description}</span>
          <h1>Arguments:</h1>
          <table className="argtable">
            <tbody>
              {Object.keys(context.args).map(function (key, i) {
                return <TableRow arg={key} blurb={context.args[key]} key={i} />
              })}
            </tbody>
          </table>
          <h1>Function: {this.props.context.function}</h1>


        </div>
    }

    return (
      <div className="infopane">
        {toDisplay}
      </div>
    );
  }
}

export default InfoPane;
