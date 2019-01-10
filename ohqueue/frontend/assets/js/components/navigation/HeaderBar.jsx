import React from "react";
import PropTypes from "prop-types";
import { Link } from 'react-router-dom'

export class HeaderBar extends React.Component {
    render() {
        return <header>
            <nav className="navbar navbar-default navbar-fixed-top">
                <div className="container">
                    <div className="navbar-header">
                    <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse-section">
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                    </button>
                    <Link className="navbar-brand" to="/queue"><strong>{ window.courseName }</strong> Queue</Link>
                    </div>
                    <div className="collapse navbar-collapse" id="navbar-collapse-section">
                    <ul className="nav navbar-nav navbar-right">

                        {(() => {
                        if (this.props.myTicket) {
                            return <li><Link to={`/queue/myTicket/`}>My Request</Link></li>;
                        }
                        })()}

                        {(() => {
                        if (this.props.currentUser != null) {
                            return (
                            <li className="dropdown">
                                <a href="#" className="dropdown-toggle" data-toggle="dropdown" role="button">{this.props.currentUser.name} <span className="caret"></span></a>
                                <ul className="dropdown-menu">
                                <li><a href="/logout/">Log out</a></li>
                                </ul>
                            </li>
                            )
                        } else {
                            return (<li><a href="/login/">Staff Login</a></li>)
                        }
                        })()}

                    </ul>
                    </div>
                </div>
                </nav>
        </header>;
    }
}

HeaderBar.propTypes = {
    links: PropTypes.array,
    active: PropTypes.string,
    changePage: PropTypes.func,
    currentUser: PropTypes.object,
    myTicket: PropTypes.object
};
