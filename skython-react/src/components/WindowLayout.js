import React, { Component } from 'react';
import List from './List.js';
import Info from './InfoPane.js';
import './style/WindowLayout.css';

class WindowLayout extends Component {

  constructor(props) {
    super(props);

    // Our initial states
    this.state = {
      "context": undefined
    }

    /* We bind these functions to this component's mounting so that they are
    allowed to setState. Quite simply, if a function must change the component
    state, we must bind it first here in the constructor. */
    this.setWindowContext = this.setWindowContext.bind(this);
  }

  // Context switcher for info pane.
  setWindowContext(context) {
    if (this.state.context && (context === this.state.context)) {
      this.setState({ "context": undefined });
    } else {
      this.setState({ "context": context });
    }
  }

  render() {
    return (
      <div>
        <div className="list">
          <List contextSwitcher={this.setWindowContext} selectedObject={this.state.context} />
        </div>
        <div className={this.state.context ? "info context" : "info nocontext"}>
          <Info context={this.state.context} />
        </div>
      </div>
    );
  }
}

export default WindowLayout;
