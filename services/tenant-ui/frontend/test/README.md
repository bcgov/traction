# Tests used while building the tenant-ui frontend

Testing the frontend consists of two distinct areas. One is testing the pinia stores. This should ensure the store functions work as expected and that they handle API responses correctly. The other area is testing ui components and that they respond as expected to user interaction. It should be ensured that expected functions are called and that changes in components visiblity or behavior don't have regressions. However testing store functions while testing the ui should be avoided to prevent duplication. Simple mocking of return values can be used to test ui components with a particular state but not the actual store function itself.

Api Mocking:

- API mocking is done using Mock Service Worker (msw). Take a look a the documentation at https://mswjs.io/.
  The file /test/setupApi.ts is used to load a mock api service. The mocked responses are found in /test/api/responses and each store has it's own response file. The routes are found in /test/api/routes and each file can have an array of successful and error paths. The successful responses are then loaded into the mock server in setupApi. Load the error responses using server.use(ErrorResponses) and they will get prepended before the success responses. The server is reset for every test file.

Global Mocking:

- The file /test/setupGlobalMocks.ts is used when a mock is needed in most files such as translation mocks. Pinia is mocked here with a test state for all the stores. Mocking a module in a test file can be used to override the global mocks if needed.

Testing Components:

- Any component that uses a pinia store should use the createTestingPinia plugin when mounting. Information can be found here https://pinia.vuejs.org/cookbook/testing.html#unit-testing-components. The stores are all loaded as global mocks so initial state shouldn't be needed but can overriden. It is then possible to alter state using the mocked config object before loading the store. There is an example of this in Login.test.

- There are several ways to test toast notifications. Currently the best way to do this is like. \
  `const wrapperVm = wrapper.vm as unknown as typeof CreateContactForm; `\
  `const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');`

- Forms are somewhat tricky. To mock them first mock useVuelidate the validation library @vuelidate/core and pass it a mock validation object. These are stored in /\_\_mocks\_\_/validation/forms.ts. There are several examples of this found in any \*\*Form.test.ts file. If the form field values are used in the component outside of a mocked function you must also mock vue itself by copying vue and overriding reactive. There is an example where this is needed in CreateMessageForm.test.ts. This could be avoided by changing the components code but is left an example as this pattern will likely be needed in the future.
