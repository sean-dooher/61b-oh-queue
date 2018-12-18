import {CHANGE_PAGE} from "../actions/navActions";

const initialState = {
    api: {},
    navbar: {
        links: [{name: 'Page 1', href: '/'}, {name: 'Page 2', href: '/page2'}],
        active: 'Page 1'
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
        default:
            return newState;
    }
}