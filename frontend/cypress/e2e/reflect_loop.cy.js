// Cypress E2E for reflection loop
it('submits reflection feedback', () => {
  cy.login();
  cy.visit('/assistants/test-assistant/reflect');
  cy.get('textarea').type('Great run');
  cy.get('select').select('5');
  cy.contains('Save').click();
  cy.contains('Reflection saved');
});
