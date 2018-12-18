import React from "react";
import PropTypes from "prop-types";
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

export class HeaderBar extends React.Component {
    render() {
        return <header>
            <div className="navbar navbar-expand-md navbar-dark bg-dark">
                <a className="navbar-brand" href="/">React Project</a>
                <button className="navbar-toggler d-lg-none" type="button" data-toggle="collapse"
                        data-target="#main-nav" aria-controls="main-dev" aria-expanded="false"
                        aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"/>
                </button>
                <div className="collapse navbar-collapse" id="main-nav">
                    <ul className="navbar-nav mr-auto">
                        {
                            this.props.links.map((link, key) => {
                                if (this.props.active === link.name) {
                                    return <li className={"nav-item active"} key={key}>
                                        <Link className="nav-link" to={link.href}>{link.name}</Link>
                                    </li>;
                                } else {
                                    return <li className={"nav-item"} key={key}>
                                        <Link className="nav-link" to={link.href}>{link.name}</Link>
                                    </li>;
                                }
                            })
                        }
                    </ul>
                </div>
            </div>
        </header>;
    }
}

HeaderBar.propTypes = {
    links: PropTypes.array,
    active: PropTypes.string,
};
