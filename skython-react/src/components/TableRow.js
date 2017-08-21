import React, { Component } from 'react';
import './style/TableRow.css';

class TableRow extends Component {
  render() {
    return (
      <tr>
        <td className="first">{this.props.arg}</td>
        <td className="sublime">{this.props.blurb}</td>
      </tr>
    );
  }
}

export default TableRow;