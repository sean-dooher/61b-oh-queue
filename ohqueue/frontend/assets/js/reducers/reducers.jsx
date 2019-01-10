import {CHANGE_PAGE} from "../actions/navActions";
import { UPDATE_TICKETS } from "../actions/ticketActions";

const initialState = {
    api: {
        tickets: [],
    },
    navbar: {
        links: [],
        active: '/queue/'
    }
};

function cloneState(oldState) {
    return JSON.parse(JSON.stringify(oldState));
}

export function mainApp(state = initialState, action) {
    let newState = cloneState(state);

    switch (action.type) {
        case CHANGE_PAGE:
            newState.navbar.active = action.page;
            return newState;
        case UPDATE_TICKETS:
            newState.api.tickets = action.tickets;
            return newState;
        default:
            return newState;
    }
}