import React, { Component } from 'react';
import './style/ListItem.css';

class ListItem extends Component {
  render() {

    var contextSwitcher = this.props.contextSwitcher;
    var description = this.props.object.description;
    var blurb = description.length > 92 ? description.substring(0,92) + "..." : description;

    return (
      <div className={this.props.object === this.props.selectedObject ? "item selected" : "item unselected"} onClick={() => contextSwitcher(this.props.object)}>
        <h1>{this.props.object.name}</h1>
        <div className = "subtext">
        <h3>{blurb}</h3>
        </div>
      </div>
    );
  }
}

export default ListItem;