import React from "react";
import PropTypes from "prop-types";
import PresenceIndicatorApi from "../../containers/contents/presenceIndicatorAPI";

export class MainView extends React.Component {
    componentWillMount() {
        this.props.refreshTickets();
    }    

    render(){
        return (
            <div>
            {/* {showJumbotron && <Jumbotron state={state}/>} */}
            <div>
              {/* <Messages messages={state.messages}/> */}
              <PresenceIndicatorApi tickets={this.props.tickets} />
              {/* {isStaff(state) && <FilterControls filter={state.filter}/>}
              {isStaff(state) && <hr />} */}
              {/* <Tabs selectedIndex={state.queueTabIndex} onSelect={selectTab}>
                <Tab label={`Waiting (${pendingTickets.length})`}>
                  <TicketList status={'pending'} state={state} />
                </Tab>
                <Tab label={`Assigned (${assignedTickets.length})`} shouldHighlight={shouldHighlightAssigned}>
                  <TicketList status={'assigned'} state={state} />
                </Tab>
              </Tabs> */}
            </div>
          </div>
        );
    }
}

MainView.propTypes = {
    tickets: PropTypes.array,
    refreshTickets: PropTypes.func
}