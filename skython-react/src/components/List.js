import React, { Component } from 'react';
import GETCatalog from './util/network.js';
import ListItem from './ListItem.js';
import './style/List.css';

class List extends Component {

  constructor(props) {
    super(props);

    // Our initial states
    this.state = {
      "lambdas": []
    }

    /* We bind these functions to this component's mounting so that they are
    allowed to setState. Quite simply, if a function must change the component
    state, we must bind it first here in the constructor. */
    this.loadLambdas = this.loadLambdas.bind(this);
  }

  /* This is called when the parent initializes this child.
  An update request is made. */
  componentWillMount() {
    this.loadLambdas();
  }

  // Updates lambdas list state field with the updated catalog.
  loadLambdas() {
    GETCatalog((response) => this.setState({ "lambdas": response }));
  }

  render() {

    // Dereference context switcher function for this list.
    var contextSwitcher = this.props.contextSwitcher;
    var selectedObject = this.props.selectedObject;
    return (
      <div className="list">
        {this.state.lambdas.map(function (object, i) {
          return <ListItem contextSwitcher={contextSwitcher} selectedObject={selectedObject} object={object} key={i}/>;
        })}
      </div>
    );
  }
}

export default List;
