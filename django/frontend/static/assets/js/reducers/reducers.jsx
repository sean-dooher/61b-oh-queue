const initialState = {
    api: {}
};

export function sentinelApp(state = initialState, action) {
    switch (action.type) {
        default:
            return state;
    }
}