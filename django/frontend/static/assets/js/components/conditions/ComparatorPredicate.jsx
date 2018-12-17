import React from "react";
import PropTypes from "prop-types";
import {LeafSelector} from "../values/LeafSelector";

export class ComparatorPredicate extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            operator: '=',
            first_format: 'bool',
        };
        this.formatChanged = this.formatChanged.bind(this);
        this.handleComparatorChange = this.handleComparatorChange.bind(this);
    }

    getOperators() {
        let operators = this.state.first_format === 'number' || this.state.first_format === 'number+units' ?
            ['=', '!=', '>', '<', '>=', '<='] : ['=', '!='];
        return (<div className="row">
            <select name="operator" className="form-control custom-select"
                    value={this.state.operator} onChange={this.handleComparatorChange}>
                {operators.map((op, key) => <option value={op} key={key}>{op}</option>)}
            </select>
        </div>);
    }

    formatChanged(newFormat) {
        this.setState({first_format: newFormat, operator: '='});
    }

    handleComparatorChange(event) {
        this.setState({operator: event.target.value});
    }

    getPredicate() {
        let first = [this._first.state.selected_leaf, this._first.state.selected_device];
        let second;
        if(this._second.state.selected_leaf === 'literal') {
            second = this.state.first_format !== 'string' ? JSON.parse(this._second.state.selected_device) : this._second.state.selected_device;
        } else {
            second = [this._second.state.selected_leaf, this._second.state.selected_device];
        }
        return [this.state.operator, first, second];
    }

    render(){
       return <div className="row">
           <div className="col-md-5">
            <LeafSelector datastores={this.props.datastores} leaves={this.props.leaves} ref={(c) => this._first = c} formatChanged={this.formatChanged}/>
           </div>
           <div className="col-md-2">
            {this.getOperators()}
           </div>
           <div className="col-md-5">
            <LeafSelector datastores={this.props.datastores} leaves={this.props.leaves} literal format={this.state.first_format} ref={(c) => this._second = c}/>
           </div>
       </div>;
    }
}

ComparatorPredicate.propTypes = {
    leaves: PropTypes.array,
    datastores: PropTypes.array
};