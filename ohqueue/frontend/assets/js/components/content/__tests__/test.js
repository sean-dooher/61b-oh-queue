import React from 'react'
import {mount, shallow} from 'enzyme'
import {PageOne} from '../page1'

test ('page one smoke', () => {
  const wrapper = mount(<PageOne/>); // mount/render/shallow when applicable
  expect(wrapper.find('h1').text()).toEqual('React has successfully been loaded!');
});
