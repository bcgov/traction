import { mount, shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import ConfigItem from '@/components/common/ConfigItem.vue';

const mountConfigItem = () =>
  mount(ConfigItem, {
    props: {
      title: 'the_header',
      content: 'the_content',
    },
    global: {
      plugins: [PrimeVue],
    },
  });

const mountConfigItemSlot = () =>
  mount(ConfigItem, {
    slots: {
      title: 'the_header',
      content: '<div>test</div>',
    },
    global: {
      plugins: [PrimeVue],
    },
  });

describe('ConfigItem', () => {
  test('mount renders with props', async () => {
    const wrapper = mountConfigItem();

    const strongTitle = wrapper.find('strong');
    const spanContent = wrapper.find('span');
    expect(strongTitle.html()).toContain('the_header');
    expect(strongTitle.html()).toContain('configDelim');
    expect(spanContent.html()).toContain('the_content');
  });

  test('mount renders with slots', async () => {
    const wrapper = mountConfigItemSlot();

    const strongTitle = wrapper.find('strong');
    const spanContent = wrapper.find('div');
    expect(strongTitle.html()).toContain('the_header');
    expect(strongTitle.html()).toContain('configDelim');
    expect(spanContent.html()).toContain('test');
  });
});
