# Tests used while building the tenant-ui frontend

Testing the frontend consists of two distinct areas. One is testing the pinia stores. This should ensure the store functions work as expected and that they handle API responses correctly. The other area is testing ui components and that they respond as expected to user interaction. It should be ensured that expected functions are called and that changes in components visiblity or behavior don't have regressions. However testing store functions while testing the ui should be avoided to prevent duplication. Simple mocking of return values can be used to test ui components with a particular state but not the actual store function itself.

Api Mocking:

- API mocking is done using Mock Service Worker (msw). Take a look a the documentation at https://mswjs.io/.
  The file /test/setupApi.ts is used to load a mock api service. The mocked responses are found in /test/api/responses and each store has it's own response file. The routes are found in /test/api/routes and each file can have an array of successful and error paths. The successful responses are then loaded into the mock server in setupApi. Load the error responses using server.use(...ErrorResponses) and they will get prepended before the success responses. The server is reset for every test file.

Global Mocking:

- The file /test/setupGlobalMocks.ts is used when a mock is needed in most files such as translation mocks. Pinia is mocked here with a test state for all the stores. Mocking a module in a test file can be used to override the global mocks if needed.

Testing Components:

- **_Important!_** Any component that uses a pinia store must mock it. If it doesn't it will fail to mount with a confusing error. When adding a new store to a component make sure that the store is mocked and loaded into pinia and @store mocks in setupGlobalMocks. If the store is new or doesn't exist add it with the required properties following the same pattern as the other store mocks and load it into pinia and @store mocks.

- **_Important!_** If a test is hanging it's probably a problem with the mocks. It can be frustrating to figure out why. Here are some tips to solve it:

  - if it is using a pinia store make sure that createTestingPinia plugin is used when mounting the component.
  - Make sure the store mock in `/test/__mocks__/store` has all the mocked functions and objects being used in the test component. If objects properties are used which don't exist in the mock they will be undefined and cause the test to hang.
  - It could missing another plugin or stub.
  - Commenting out template code one block from the inside out at a time can help narrow down the problem and see exceptions.
  - If it is still really hard to get right it might be better to test inner components seperatly or only do a shallow mount on parent object.

- There are several ways to test notifications and popups are triggered. The best way to do this seems to be: \
  `const wrapperVm = wrapper.vm as unknown as typeof CreateConnectionForm; `

  `const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');` \
  `expect(toastInfoSpy).toHaveBeenCalled();`

  `const requireSpy = vi.spyOn(wrapperVm.confirm, 'require');` \
  `expect(requireSpy).toHaveBeenCalled();`

- You can use the primevue/confirmationservice plugin to avoid mocking primevue/useconfirm manually.

- Forms are somewhat tricky. To mock them first mock useVuelidate the validation library @vuelidate/core and pass it a mock validation object. These are stored in /\_\_mocks\_\_/validation/forms.ts. There are several examples of this found in any \*\*Form.test.ts file. If the form field values are used in the component outside of a mocked function you must also mock vue itself by copying vue and overriding reactive. There is an example where this is needed in CreateMessageForm.test.ts. This could be avoided by changing the components code but is left an example as this pattern will likely be needed in the future.
